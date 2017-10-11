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
    try:
        length = response.headers['content-length']
    except KeyError:
        return True
    else:
        if length == '0':
            get_new_token()
            save_token()
        return False


def save_token():
    with open(_TOKEN_FILE, 'w') as file:
        file.write(_token)


def get_auth_header():
    return {'Authorization': _token}


def get_new_token():
    response = requests.post(url=get_api_resource_url('login'), json=get_login_request_body())
    auth_token = response.headers['Authorization']
    global _token
    _token = auth_token
