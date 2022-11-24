import asyncio
import sys
import logging
import shutil
import json
sys.path.append('/app')
from process_image import detect_object_deepstack, detect_object_coral
import timestamp

config = json.loads('{"deepstack_url": "10.0.0.12", "object": "person", "add_labels": "true", "threshold": 0.7}')
async def test_process():
  await copy_photo()
  now = timestamp.now()
  print(type(config))
  image =  ["photos/test-result.jpeg", "photos/test.jpeg", now, "success"]
  detection = await detect_object_deepstack("10.0.0.12", image, "person", "true", 0.7)
  return detection

async def copy_photo():
  shutil.copyfile("photos/template.jpeg", "photos/test.jpeg")
test = asyncio.run(test_process())
print(test)
assert test["success"], "detection was not successful"
assert test["label"] == "person", "object in image not detected"
assert test["confidence"] >= .7, "confidence threshold not working"