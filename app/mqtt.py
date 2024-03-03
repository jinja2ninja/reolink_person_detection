import paho.mqtt.client as mqtt
import logging
import json

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.debug("Connected to MQTT broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection
    else:
        logging.debug("MQTT Connection failed")

def publish_detection(mqtt_config, camera, detection):
  logging.debug(f"{mqtt_config}")
  detection_json = json.dumps(detection)
  mqtt_client= mqtt.Client(mqtt_config['client_name'])
  mqtt_client.username_pw_set(mqtt_config['user'], mqtt_config['password'])                        #create client object
  mqtt_client.on_connect= on_connect
  mqtt_client.connect(mqtt_config['broker'],mqtt_config['port'])
  mqtt_client.publish(f"{mqtt_config['topic']}/{camera}", detection_json)
