import subprocess
import requests
import auth
from requests_utils import get_headers, get_api_resource_url


def _get_ip():
    return subprocess.run('hostname -I', shell=True, check=True, stdout=subprocess.PIPE).stdout.decode('UTF-8').rstrip()


def send_ip():
    try:
        response = requests.put(url=get_api_resource_url('ip'), headers=get_headers(json=True, auth=True),
                                json={'ip': ip})
    except requests.exceptions.RequestException as e:
        print(e)
        send_ip()
    else:
        if not auth.validate_response(response):
            send_ip()


ip = _get_ip()
