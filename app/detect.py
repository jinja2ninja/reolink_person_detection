import asyncio
import read_config
from grab_jpeg import grab_jpeg
from reset_directories import reset_directories
from process_image import detect_object_deepstack, detect_object_coral
import logging
from write_row import write_row
from mqtt import publish, on_connect

config = read_config.read_config()
cameras = config["cameras"]
logging.basicConfig()
logging.getLogger().setLevel(config["log"])
db_config = {'password': config['database']['password'], 'db': config['database']['db'], 'host': config['database']['host'], 'user': config['database']['user']}
mqtt_config = {'client_name': config['mqtt']['client_name'],'topic': config['mqtt']['topic'], 'user':  config['mqtt']['user'], 'password':  config['mqtt']['password'], 'broker': config['mqtt']['broker'], 'port': config['mqtt']['port']}
async def main():
  for item in cameras:
    logging.info(item)
    reset_directories(config["directory"], item)
    image =  await grab_jpeg(item, cameras[item]["ip"], cameras[item]["pass"], cameras[item]["user"], config["directory"], config["log"], config["timeout"])
    if config['method'] == "deepstack":
      logging.debug(f"using method {config['method']}")
      detection = await detect_object_deepstack(config['deepstack_url'], image, config['object'], config['add_labels'])
    elif config['method'] == "coral":
      logging.debug(f"using method {config['method']}")
      detection = await detect_object_coral(config["labels"], config["model"], image, cameras[item]["count"], cameras[item]["threshold"], config["object"], config["add_labels"])
    logging.debug(detection)
    try:
      write_row(db_config, detection, item)
      logging.debug(detection)
      try:
        publish(mqtt_config, item, detection)
      except: 
        pass
    except:
      logging.debug(f"no row added to database")

while True:
  if __name__ == '__main__':
    asyncio.run(main())
    
