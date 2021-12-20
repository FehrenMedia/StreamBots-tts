import paho.mqtt.client as mqtt
import pyttsx3
import json
import datetime
import os

mqtt_hostname = os.environ['mqtt_hostname']
mqtt_username = os.environ['mqtt_username']
mqtt_password = os.environ['mqtt_password']


def tts_say(text : str, sprache = 'de'):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # setting up new voice rate
        voices = engine.getProperty('voices')  # getting details of current voice
        if sprache == 'en':
            engine.setProperty('voice', voices[1].id)
        elif sprache == 'de':
            engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()
        engine.startLoop(False)
        # engine.iterate() must be called inside Server_Up.start()
        engine.endLoop()
    except Exception as e:
        print(e)
        pass


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("smartBots/tts/say")
    #client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8")
    print(f'topic: {topic} --- msg: {payload}')
    if topic == "smartBots/tts/say":
        try:
            data = json.loads(str(payload))
            lang = data.get("lang", "de")
            text = data.get("text")
            print(text)
            if text == None:
                client.publish("smartBots/tts/feedback", json.dumps({"timestamp": int(datetime.datetime.now().timestamp()), "status": "failed", "error": "No Text"}))
            else:
                tts_say(text, lang)
                client.publish("smartBots/tts/feedback", json.dumps({"text": text, "lang": lang,"timestamp": int(datetime.datetime.now().timestamp()), "status" : "success", "error" : None}))
        except Exception as e:
            print(e)
            client.publish("smartBots/tts/feedback", json.dumps({"timestamp": int(datetime.datetime.now().timestamp()), "status" : "failed", "error" : e}))
            pass


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username=mqtt_username,password=mqtt_password)
client.connect(mqtt_hostname, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

