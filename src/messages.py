import threading
from collections import deque
import auth
import requests
import time
import events
import threads
from requests_utils import get_headers, get_api_resource_url

LOAD_NEW_MESSAGES_RATE = 20


def _get_messages_url(resource=''):
    return '{0}/{1}'.format(get_api_resource_url('messages'), resource)


def _get_last_id():
    try:
        response = requests.get(url=_get_messages_url('read'), headers=get_headers(auth=True))
    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(15)
        return _get_last_id()
    else:
        if auth.validate_response(response):
            data = response.json()
            return int(data['lastReadId'])
        else:
            return _get_last_id()


def _get_new_messages():
    try:
        response = requests.get(url=_get_messages_url('from/{}'.format(last_received_id)),
                                headers=get_headers(auth=True))
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        if auth.validate_response(response):
            return response.json()
        else:
            return _get_new_messages()


def load_messages():
    global messages_to_read, last_received_id
    while True:
        new_messages = _get_new_messages()
        if new_messages:
            messages_to_read.extend(new_messages)
            if not threads.thread_flow.isAlive() and not events.reading_message.is_set():
                threads.start_flow()
            last_received_id = new_messages[-1]['id']
        time.sleep(LOAD_NEW_MESSAGES_RATE)


def setup_messages_service():
    threading.Thread(target=load_messages, daemon=True).start()


def send_read_id(read):
    try:
        response = requests.put(url=_get_messages_url('read'), headers=get_headers(json=True, auth=True),
                                json={'lastReadId': read})
    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(LOAD_NEW_MESSAGES_RATE)
        send_read_id(read)
    else:
        if not auth.validate_response(response):
            send_read_id(read)


last_received_id = _get_last_id()
messages_to_read = deque()
