import requests
import threading
import time
from collections import deque


def _get_messages_url(resource):
    return "http://api.adamklimko.pl/raspberry/messages/{}".format(resource)


def _get_last_id():
    response = requests.get(url=_get_messages_url('read'))
    data = response.json()
    return int(data['lastReadId'])


def _get_new_messages():
    return requests.get(url=_get_messages_url('from/{}'.format(last_received_id))).json()


def load_messages():
    global messages_to_read, last_received_id
    new_messages = _get_new_messages()
    if new_messages:
        messages_to_read.extend(new_messages)
        last_received_id = new_messages[-1]['id']
    threading.Timer(20, load_messages).start()


def set_read_id(read):
    requests.put(url=_get_messages_url('read'), headers={'Content-Type': 'application/json'},
                 json={'lastReadId': read})


last_received_id = _get_last_id()
messages_to_read = deque()
