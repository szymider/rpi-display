import subprocess
import requests


def get_ip():
    return subprocess.run('hostname -I', shell=True, check=True, stdout=subprocess.PIPE).stdout.decode('UTF-8').rstrip()


def send_ip():
    requests.put(url="http://api.adamklimko.pl/raspberry/ip", headers={'Content-Type': 'application/json'},
                 json={"ip": ip})


ip = get_ip()
