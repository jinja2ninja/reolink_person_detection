import logging
import urllib.request
import socket
import requests
import timestamp
import time
from PIL import Image, ImageDraw, ImageFont, ImageFile
from PIL import UnidentifiedImageError
import os
from draw_objects import draw_objects_coral, draw_objects_deepstack
from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
ImageFile.LOAD_TRUNCATED_IMAGES = True
import asyncio

async def detect_object_coral(labels, model, input_image, count, threshold, thing, add_labels):
  labels = read_label_file(labels) if labels else {}
  interpreter = make_interpreter(model)
  interpreter.allocate_tensors()
  try:
    image = Image.open(input_image[1])
  except UnidentifiedImageError:
    image = "null"
  except FileNotFoundError:
      image = "null"
  if image == "null":
    success = False
    logging.debug(f"invalid image from camera")
    os.remove(input_image[1])  
  else:
    _, scale = common.set_resized_input(
        interpreter, image.size, lambda size: image.resize(size, Image.ANTIALIAS))
    for _ in range(count):
      start = time.perf_counter()
      interpreter.invoke()
      inference_time = time.perf_counter() - start
      objs = detect.get_objects(interpreter, threshold, scale)  
      logging.debug(f"{objs}")
      if not objs:
        success = False
        logging.debug(f"No objects detected, deleting {input_image[1]}")
        #os.remove(input_image[1])
      else:
        logging.debug("success")
        success = True
        for obj in objs:
          label = (labels.get(obj.id))
          logging.debug(label)
          if label == thing:      
            logging.debug("yes")
            confidence = round((obj.score * 100))
            xmax = obj.bbox.xmax
            xmin = obj.bbox.xmin
            ymax =  obj.bbox.ymax
            ymin = obj.bbox.ymin
          
            filename = input_image[0]
            filename_tmp = input_image[1]
            now = input_image[2]
            detection = {'predictions': [{'x_max': xmax, 'x_min': xmin, 'y_max': ymax,  'y_min': ymin, 'label': label, 'confidence': confidence }], 'success': success}
            logging.debug(f"Object Detected! File saved as {input_image[0]}")
            logging.debug(f"Detection details: {detection}")
            draw_objects_coral(objs, input_image, label, add_labels)
            #os.remove(filename_tmp)
            return {'label': thing, 'confidence': confidence, 'ymincoord': ymin, 'ymaxcoord': ymax, 'xmincoord': xmin, 'xmaxcoord': xmax, 'timestamp': now, 'filename': filename, 'success': success}
          else:
            logging.debug(f"{label}    {thing}")
            success = False
            logging.debug(f"No objects detected, deleting {input_image[1]}")
            try:
              logging.debug("this is a test")
            except:
              logging.debug(f"unable to delete {input_image[1]}")


async def detect_object_deepstack(deepstack_url, input_image, object, add_labels):
  image_data = open(input_image[1],"rb").read()
  response = requests.post(f"http://{deepstack_url}:5000/v1/vision/detection",files={"image":image_data}).json()
  label_index = -1
  try: 
      pred = iter(response['predictions'])
  except KeyError:
      logging.warning("invalid response from deepstack, waiting 10 seconds and trying again")
      sleep(10)
      response = requests.post(f"http://{deepstack_url}:5000/v1/vision/detection",files={"image":image_data},min_confidence={threshold}).json()
      pred = iter(response['predictions'])
  while True:
    try:
      element = next(pred)
      if object not in element['label']:
        label_index += 1
        success = False
      elif object  in element['label']:
        label_index += 1
        confidence = element['confidence']
        xmin = response['predictions'][label_index]['x_min']
        xmax = response['predictions'][label_index]['x_max']
        ymin = response['predictions'][label_index]['y_min']
        ymax = response['predictions'][label_index]['y_max']
        logging.debug(f"confidence is {confidence}")
        # create variables for square boundaries
        draw_objects_deepstack(response, input_image, label_index, add_labels)
        os.remove(input_image[1])
        success = True
        object = response['predictions'][label_index]['label']
        detection = {'predictions': [{'x_max': xmax, 'x_min': xmin, 'y_max': ymax,  'y_min': ymin, 'label': object, 'confidence': confidence }], 'success': success}
        logging.debug(f"Detection details: {response}")
        now = input_image[2]
        #return object, confidence, ymin, ymax, xmin, xmax, now, input_image[1], success
        return {'label': object, 'confidence': confidence, 'ymincoord': ymin, 'ymaxcoord': ymax, 'xmincoord': xmin, 'xmaxcoord': xmax, 'timestamp': now, 'filename': input_image, 'success': success}
        break
    except StopIteration:
      break
  