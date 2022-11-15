import requests
import shutil 
import timestamp
import logging
import read_config
import asyncio

async def grab_jpeg(camera_friendly, camera_ip, camera_pass, camera_user, directory, log_level, timeout):
  logging.basicConfig()
  logging.getLogger().setLevel(log_level)  
  image_url = f"http://{camera_ip}/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUCeI9WG7C&user={camera_user}&password={camera_pass}"

  try: 
    response = requests.get(image_url, stream = True, timeout = timeout)
  except requests.exceptions.ConnectTimeout: 
    response = "timeout"


  if response == "timeout":
        logging.warning(f"Image Couldn\'t be retreived from camera {camera_friendly}, reason: timeout")
        logging.warning(f"Consider increasing the timeout variable and make sure that your connection variables are valid")

  elif response.status_code == 200:
      now = timestamp.now()
      filename = f"{directory}{camera_friendly}/{now}.jpeg" # put them in the camera's /tmp directory to be processed
      filename_tmp = f"{directory}{camera_friendly}/.tmp/{now}.jpeg" # put them in the camera's /tmp directory to be processed 
      response.raw.decode_content = True
      with open(filename_tmp,'wb') as f:
          shutil.copyfileobj(response.raw, f)
      return filename, filename_tmp, now, "success"

  else:
      logging.warning(f"Image Couldn\'t be retreived from camera {camera_friendly}, reason: unknown")
      now = timestamp.now()
      filename = "null"
      filename_tmp = "null"
      return filename, filename_tmp, now, "failure"