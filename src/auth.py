import time
import requests
from login import get_login_request_body
from requests_utils import get_api_resource_url

_TOKEN_FILE = '/home/pi/zeroseg/jwt_token'


def get_token_from_file():
    with open(_TOKEN_FILE) as file:
        token = file.readline()
    return token


_token = get_token_from_file()


def validate_response(response):
    if response.status_code == requests.codes.ok:
        return True
    else:
        get_new_token()
        save_token()
        return False


def save_token():
    with open(_TOKEN_FILE, 'w') as file:
        file.write(_token)


def get_auth_header():
    return {'Authorization': _token}


def get_new_token():
    try:
        response = requests.post(url=get_api_resource_url('login'), json=get_login_request_body())
    except requests.exceptions.RequestException:
        time.sleep(15)
        get_new_token()
    else:
        auth_token = response.json()['token']
        global _token
        _token = auth_token
