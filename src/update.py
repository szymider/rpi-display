import requests
import threading
import time
from constants import *
from requests_utils import get_response_json

temperature = 0

eur = 0
usd = 0

followers = 0


def _weather():
    while True:
        try:
            data = get_response_json(url=URL_WEATHER)
        except requests.exceptions.RequestException as e:
            print(e)
        else:
            global temperature
            temperature = int(round(data['current_observation']['temp_c']))
        time.sleep(UPDATE_RATE_WEATHER)


def _currency():
    while True:
        try:
            data_eur = get_response_json(url=URL_EUR)
            data_usd = get_response_json(url=URL_USD)
        except requests.exceptions.RequestException as e:
            print(e)
        else:
            global eur, usd
            eur = int(round(data_eur['rates'][0]['mid'], 2) * 100)
            usd = int(round(data_usd['rates'][0]['mid'], 2) * 100)
        time.sleep(UPDATE_RATE_CURRENCY)


def _instagram():
    while True:
        try:
            data = get_response_json(url=URL_IG)
        except requests.exceptions.RequestException as e:
            print(e)
        else:
            global followers
            followers = data['user']['followed_by']['count']
        time.sleep(UPDATE_RATE_IG)


def all_modes():
    threading.Thread(target=_weather, daemon=True).start()
    threading.Thread(target=_currency, daemon=True).start()
    threading.Thread(target=_instagram, daemon=True).start()
