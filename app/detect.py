import asyncio
import read_config
from grab_jpeg import grab_jpeg
from reset_directories import reset_directories
from process_image import detect_object_deepstack, detect_tpu
import logging
from write_row import write_row
from mqtt import publish_detection, on_connect
import os
import threading
import time

log_level = os.environ['DETECTOR_LOG']
config = read_config.read_config(log_level)
cameras = config["cameras"]
logging.basicConfig()
logging.getLogger().setLevel(config["log"])
db_config = {'password': config['database']['password'], 'db': config['database']['db'], 'host': config['database']['host'], 'user': config['database']['user']}
mqtt_config = {'client_name': config['mqtt']['client_name'],'topic': config['mqtt']['topic'], 'user':  config['mqtt']['user'], 'password':  config['mqtt']['password'], 'broker': config['mqtt']['broker'], 'port': config['mqtt']['port']}
async def main():
  logging.debug(f"Configured cameras:   {cameras}")
  start = time.time()
  for camera in cameras:
    reset_directories(config["directory"], camera)
    image =  await grab_jpeg(camera, cameras[camera]["ip"], cameras[camera]["pass"], cameras[camera]["user"], config["directory"], config["log"], config["timeout"])
    if config['method'] == "deepstack":
      logging.debug(f"using method {config['method']}")
      detection = await detect_object_deepstack(config['deepstack_url'], image, config['object'], config['add_labels'], cameras[camera]["threshold"])
    elif config['method'] == "coral":
      logging.debug(f"using method {config['method']}")
      tpu0_thread = threading.Thread(
          target=detect_tpu,
          args=(db_config, camera, config["log"], config["labels"], config["model"], image, cameras[camera]["count"], cameras[camera]["threshold"], config["object"], config["add_labels"], ':1'))
      tpu1_thread = threading.Thread(
          target=detect_tpu,
          args=(db_config, camera, config["log"], config["labels"], config["model"], image, cameras[camera]["count"], cameras[camera]["threshold"], config["object"], config["add_labels"], ':1'))
      result = [None]
      tpu0_thread.start()
      tpu1_thread.start()
      tpu0_thread.join()
      tpu1_thread.join()
      end = time.time()
      run_time = end - start
      logging.debug(f"run time was: {run_time}")

while True:
  if __name__ == '__main__':
    asyncio.run(main())