import os
import time
import json
import datetime

# Need to get the MAC adress
import uuid


"""
This is a basic test script that aims to show how to communicate with
event2io and io2key hooks. In other words, this script acts as a very
minimal version of the main pipeline of CEL-APUS. Here, instead of sending
the trigger message only, a json string is sent. This one contains:
- a timestamps
- a payload (which contains) :
        - a device ID which is the MAC adress of the device
        - a message that will trigger of a gpio event
"""

write_path = "/home/cellari/cel-apus/event2io/pipe.in"
read_path = "/home/cellari/cel-apus/event2io/pipe.out"

wf = os.open(write_path, os.O_SYNC | os.O_CREAT | os.O_RDWR)
rf = None

timestamp = str(datetime.datetime.now())
# get MAC address
mac_addr = str(hex(uuid.getnode()))

# Basic loop that ask 11 times user-input
for i in range(1, 11):
    msg = input("Message ? ")

    # This statement purpose is to check if the io2key works
    # correctly. Since switch can send a specific keystroke when
    # pressed this hook, a specific message can be send through the
    # payload to trigger afterward a function in event2io
    # Since in the io2key's config file button press triggers <b> key
    # press, equality with <b> is tested here

    if msg == "b":
        payload = {"id": mac_addr, "message": "sys_ready"}
        x = {"timestamps": timestamp, "payload": payload}
        msg = str.encode(json.dumps(x))
        len_send = os.write(wf, msg)
        print("sent : ", msg)
    # This statement purpose is to send keyboard inputs through the paylaod.
    else:
        payload = {"id": mac_addr, "message": msg}
        x = {"timestamps": timestamp, "payload": payload}
        msg = str.encode(json.dumps(x))
        len_send = os.write(wf, msg)
        print("sent : ", msg)

    if rf is None:
        rf = os.open(read_path, os.O_RDONLY)

    s = os.read(rf, 4096)
    if len(s) == 0:
        break

    time.sleep(1)

os.write(wf, str.encode("exit"))
os.close(rf)
os.close(wf)
