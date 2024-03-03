import os
import logging
import yaml
import json
from vault_secrets import get_secrets

def read_config():
  logging.basicConfig()
  logging.getLogger().setLevel("DEBUG")
  try: 
    os.environ['DETECTOR_CONFIG_METHOD'] == "env"
    config_from_env = True
  except KeyError: 
    config_from_env = False
  if config_from_env:
    vault_address = os.environ['VAULT_ADDR']
    secrets = get_secrets(vault_address)
    logging.info (secrets)
    config = {
      'database': {'password': secrets['data']['data']['pg_pass'], 'user': secrets['data']['data']['pg_user'], 'db': os.environ['DETECTOR_DB'], 'host': secrets['data']['data']['pg_host']}, 
      'mqtt': {'port': int(os.environ['DETECTOR_MQTT_PORT']), 'user': secrets['data']['data']['mqtt_user'], 'password': secrets['data']['data']['mqtt_pass'], 'broker': secrets['data']['data']['mqtt_host'], 'topic': os.environ['DETECTOR_MQTT_TOPIC'], 'client_name': os.environ['DETECTOR_MQTT_CLIENT_NAME']},
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
