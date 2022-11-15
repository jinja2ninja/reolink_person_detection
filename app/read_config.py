import os
import logging
import yaml
import json

def read_config():
  logging.basicConfig()
  logging.getLogger().setLevel("DEBUG")
  with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
  return config
  logging.debug(f"config loaded: '{config}'")

