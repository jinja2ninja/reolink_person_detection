import os
import logging
import yaml
import json

def read_config():
  logging.basicConfig()
  logging.getLogger().setLevel("DEBUG")
  try: 
    os.environ['DETECTOR_CONFIG_METHOD'] == "env"
    config_from_env = True
  except KeyError: 
    config_from_env = False
  if config_from_env:
    config = {
      'database': {'password': os.environ['DETECTOR_DB_PASS'], 'user': os.environ['DETECTOR_DB_USER'], 'db': os.environ['DETECTOR_DB'], 'host': os.environ['DETECTOR_DB_HOST']}, 
      'mqtt': {'port': os.environ['DETECTOR_MQTT_PORT'], 'user': os.environ['DETECTOR_MQTT_USER'], 'password': os.environ['DETECTOR_MQTT_PASSWORD'], 'broker': os.environ['DETECTOR_MQTT_BROKER'], 'topic': os.environ['DETECTOR_MQTT_TOPIC'], 'client_name': os.environ['DETECTOR_MQTT_CLIENT_NAME']},
      'directory': os.environ['DETECTOR_DIRECTORY'],
      'interval': os.environ['DETECTOR_INTERVAL'],
      'model': os.environ['DETECTOR_MODEL'],    
      'object': os.environ['DETECTOR_OBJECT'],
      'labels': os.environ['DETECTOR_LABELS'],
      'method': os.environ['DETECTOR_METHOD'],
      'deepstack_url': os.environ['DETECTOR_DEEPSTACK_URL'],
      'add_labels': os.environ['DETECTOR_ADD_LABELS'],
      'log': os.environ['DETECTOR_LOG'],
      'timeout': int(os.environ['DETECTOR_TIMEOUT']),
      'cameras': {}
      }
    for item in os.environ:
      if "DETECTOR_CAMERA_" in item:
        config['cameras'][(item.replace("DETECTOR_CAMERA_" , "").lower())] = json.loads(os.environ[item]) #.lstrip('\"').rstrip('\"')
        logging.debug(config)
  elif not config_from_env:
    with open('config.yaml') as f:
      config = yaml.load(f, Loader=yaml.FullLoader)
  return config
  logging.debug(f"config loaded: '{config}'")
