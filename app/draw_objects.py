from PIL import Image, ImageDraw, ImageFont
import logging
def draw_objects_coral(objs, input_image, label, add_labels): # fix this up so that we're passing in a set of coordinates instead of obj
  """Draws the bounding box and label for each object."""
  for obj in objs:
    if add_labels == 'True':
      xmax = obj.bbox.xmax
      xmin = obj.bbox.xmin
      ymax =  obj.bbox.ymax
      ymin = obj.bbox.ymin
      top = [(xmin, ymin), (xmax, ymin)]
      left = [(xmin, ymin), (xmin, ymax)]
      right = [(xmax, ymin), (xmax, ymax)]
      bottom = [(xmin, ymax), (xmax, ymax)]
      img = Image.open(input_image[1])
      img1 = ImageDraw.Draw(img)
      img1.line(top, fill ="yellow", width = 5)
      img1.line(left, fill ="yellow", width = 5)
      img1.line(right, fill ="yellow", width = 5)
      img1.line(bottom, fill ="yellow", width = 5)
      font = ImageFont.truetype("qaz.ttf", 35)
      img1.text((xmax - 100, ymax - 200), label, (155, 250, 0), font)
      logging.debug(f"saving image")
      img.save(input_image[0])
    else:
      img = Image.open(input_image[1])
      img.save(input_image[0])

def draw_objects_deepstack(response, input_image, label_index, add_labels):
  xmin = response['predictions'][label_index]['x_min']
  xmax = response['predictions'][label_index]['x_max']
  ymin = response['predictions'][label_index]['y_min']
  ymax = response['predictions'][label_index]['y_max']
  # define shape of square with values from deepstack
  top = [(xmin, ymin), (xmax, ymin)]
  left = [(xmin, ymin), (xmin, ymax)]
  right = [(xmax, ymin), (xmax, ymax)]
  bottom = [(xmin, ymax), (xmax, ymax)]
  # open image for processing
  img = Image.open(input_image[1])
  # draw square shape on image
  if add_labels == 'True':
    img1 = ImageDraw.Draw(img)
    img1.line(top, fill ="yellow", width = 5)
    img1.line(left, fill ="yellow", width = 5)
    img1.line(right, fill ="yellow", width = 5)
    img1.line(bottom, fill ="yellow", width = 5)
    font = ImageFont.truetype("qaz.ttf", 35)
    img1.text((xmax - 100, ymax - 200), response['predictions'][label_index]['label'], (155, 250, 0), font)
    logging.debug(f"saving image")
    img.save(input_image[0])
  else:
    img = Image.open(input_image[1])
    img.save(input_image[0])