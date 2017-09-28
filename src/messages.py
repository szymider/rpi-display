import requests
import threading
import time
from collections import deque


def get_messages_url(resource):
    return "http://api.adamklimko.pl/raspberry/messages/{}".format(resource)


def get_last_id():
    response = requests.get(url=get_messages_url('read'))
    data = response.json()
    return int(data['latestReadId'])


def get_new_messages():
    return requests.get(url=get_messages_url('from/{}'.format(last_received_id))).json()


def load_messages():
    global messages_to_read, last_received_id
    new_messages = get_new_messages()
    if new_messages:
        messages_to_read.extend(new_messages)
        last_received_id = new_messages[-1]['id']
    else:
        print("No new messages")
    threading.Timer(10, load_messages).start()


last_read_id = last_received_id = get_last_id()
messages_to_read = deque()
load_messages()

while True:
    time.sleep(60)
