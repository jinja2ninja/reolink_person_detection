import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Connection failed")

def publish(mqtt_config, camera, detection):
  mqtt_client= mqtt.Client(mqtt_config['client_name'])   
  mqtt_client.username_pw_set(mqtt_config['user'], mqtt_config['password'])                        #create client object
  mqtt_client.on_connect= on_connect
  mqtt_client.connect(mqtt_config['broker'],mqtt_config['port'])  
  mqtt_client.publish(f"{mqtt_config['topic']}/{camera}",f"{detection}")
