import asyncio
import read_config
from grab_jpeg import grab_jpeg
from reset_directories import reset_directories
from process_image import detect_object_deepstack, detect_object_coral
import logging
from write_row import write_row

config = read_config.read_config("DEBUG")
cameras = config["cameras"]
logging.basicConfig()
logging.getLogger().setLevel(config["log"])
db_params = {'password': config['database']['password'], 'db': config['database']['db'], 'host': config['database']['host'], 'user': config['database']['user']}

async def main():
  for item in cameras:
    logging.info(item)
    reset_directories(config["directory"], item)
    image =  await grab_jpeg(item, cameras[item]["ip"], cameras[item]["pass"], cameras[item]["user"], config["directory"], config["log"], config["timeout"])
    detection = await detect_object_coral(config["labels"], config["model"], image, cameras[item]["count"], cameras[item]["threshold"], config["object"], config["add_labels"])
    print(detection)
    try:
      write_row(db_params, detection, item)
      logging.debug(detection)
    except:
      print("nothing detected")

while True:
  if __name__ == '__main__':
    asyncio.run(main())
    
