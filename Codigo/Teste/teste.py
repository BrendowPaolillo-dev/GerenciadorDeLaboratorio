import cayenne.client
import time
import credentials

credentials = credentials.Credentials()
MQTT_USERNAME  = credentials.username
MQTT_PASSWORD  = credentials.password
MQTT_CLIENT_ID = credentials.clientID

def on_message(message):
  print("message received: " + str(message))
  # If there is an error processing the message return an error string, otherwise return nothing.

client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)
# For a secure connection use port 8883 when calling client.begin:
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, port=8883)

i=0
timestamp = 0

while True:
  client.loop()

  if (time.time() > timestamp + 10):
    client.celsiusWrite(1, i)
    client.luxWrite(2, i*10)
    client.hectoPascalWrite(3, i+800)
    timestamp = time.time()
    i = i+1