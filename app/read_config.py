import os
import logging
import yaml
import json

def read_config(log_level):
  logging.basicConfig()
  logging.getLogger().setLevel(log_level)
  with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
  return config
  logging.debug(f"config loaded: '{config}'")

config = read_config("DEBUG")
# accessing config items
#print(config["cameras"]["front_door"]["camera_id"])