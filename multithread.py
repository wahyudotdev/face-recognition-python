import paho.mqtt.client as mqtt
import csv
import time
import os
import threading
from threading import Lock, Thread
import numpy as np
from numpy import savetxt

def on_connect(client, userdata, flags, rc):
    print("Connected")
    client.subscribe("imu")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    split = payload.split(",")
    # print(split)
    with open('data.csv', 'a+') as file:
        writer = csv.writer(file)
        writer.writerow([split[0],split[1],split[2]])
        readLine.close()
def save():
    count = 0
    while True:
        time.sleep(1)
        lock.acquire()
        try:
            now = time.time()
            data = np.genfromtxt('data.csv',delimiter=',')
            savetxt(f'datasets/jalan/{now}.csv',data,delimiter=',')
            print("saved")
            os.remove('data.csv')
        except Exception as e:
            print(e)
        finally:
            lock.release()
            count = count+1
            print(f"Task number : {count}")
def start():
    client.loop_forever()

client = mqtt.Client()
client.username_pw_set("wahyu", "kenari123")
client.on_connect = on_connect
client.on_message = on_message
client.connect("127.0.0.1", 1883, 60)

lock = Lock()
try:
    threads = []
    threads.append(threading.Thread(target=start))
    threads.append(threading.Thread(target=save))
    for t in threads:
        t.start()
except:
    print("unable to start thread")
while 1:
    pass