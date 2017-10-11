import requests


def get_response_json(url):
    return requests.get(url=url).json()


def get_headers(json=False, auth=False):
    from auth import get_auth_header
    headers = {}
    if json:
        headers.update({'Content-Type': 'application/json'})
    if auth:
        headers.update(get_auth_header())
    return headers


def get_api_resource_url(resource=""):
    return "http://api.adamklimko.pl/raspberry/{}".format(resource)
