import threading
import time
import requests
import subprocess
from datetime import datetime

import RPi.GPIO as GPIO
import ZeroSeg.led as led

from constants import *


def display_clock():
    while not next_mode.is_set():
        now = datetime.now()
        device.write_text(1, " {:%H%M%S}".format(now.time()), dots=(3, 5))
        next_mode.wait(DISPLAY_RATE_CLOCK)


def display_date():
    while not next_mode.is_set():
        now = datetime.now()
        device.write_text(1, "{:%d-%m-%y}".format(now.date()))
        next_mode.wait(DISPLAY_RATE_DATE)


# TODO: change displaying temperature to consider negative temperature values
def display_weather():
    while not next_mode.is_set():
        device.write_text(1, "{0}*C{1}*C".format(update_weather.temperature, update_weather.feelslike), dots=[4])
        next_mode.wait(DISPLAY_RATE_WEATHER)


# TODO: pack this code within while to one function
def display_currency():
    while not next_mode.is_set():
        device.write_text(1, " {:d} EUR".format(update_currency.eur), dots=[6])
        next_mode.wait(DISPLAY_RATE_CURRENCY)
        if not next_mode.is_set():
            device.write_text(1, " {:d} USD".format(update_currency.usd), dots=[6])
            next_mode.wait(DISPLAY_RATE_CURRENCY)


def display_instagram():
    while not next_mode.is_set():
        device.write_text(1, "IG{:>6}".format(update_instagram.followers))
        next_mode.wait(DISPLAY_RATE_IG)


def get_response_json(url):
    return requests.get(url=url).json()


def update_weather():
    try:
        data = get_response_json(url=URL_WEATHER)
        update_weather.temperature = str(int(round(data["current_observation"]["temp_c"])))
        update_weather.feelslike = str(int(round(float(data["current_observation"]["feelslike_c"]))))
        print("Weather updated")
    except requests.exceptions.RequestException as e:
        print(e)

    threading.Timer(UPDATE_RATE_WEATHER, update_weather).start()


def update_currency():
    try:
        data_eur = get_response_json(url=URL_EUR)
        update_currency.eur = int(round(data_eur["rates"][0]["mid"], 2) * 100)

        data_usd = get_response_json(url=URL_USD)
        update_currency.usd = int(round(data_usd["rates"][0]["mid"], 2) * 100)
        print("Currency updated")
    except requests.exceptions.RequestException as e:
        print(e)

    threading.Timer(UPDATE_RATE_CURRENCY, update_currency).start()


def update_instagram():
    try:
        data = get_response_json(url=URL_IG)
        update_instagram.followers = str(data["user"]["followed_by"]["count"])
        print("Instagram followers updated")
    except requests.exceptions.RequestException as e:
        print(e)

    threading.Timer(UPDATE_RATE_IG, update_instagram).start()


def brightness_flow():
    while not brightness_flow_mode.is_set():
        for intensity in range(1, 16):
            device.brightness(intensity)
            brightness_flow_mode.wait(0.1)
        brightness_flow_mode.wait(0.05)
        for intensity in range(15, 0, -1):
            device.brightness(intensity)
            brightness_flow_mode.wait(0.1)
        brightness_flow_mode.wait(0.05)
    brightness_flow_mode.clear()


def brightness_dependent_on_time():
    while not brightness_dependent_on_time_mode.is_set():
        hour = datetime.now().hour
        for hour_threshold in HOURS.keys():
            if hour <= hour_threshold:
                device.brightness(HOURS[hour_threshold])
                break
        brightness_dependent_on_time_mode.wait(300)
    brightness_dependent_on_time_mode.clear()


def button_listener():
    global current_mode
    global thread_flow, thread_dependent_on_time
    while True:
        if not GPIO.input(BUTTON_1):
            if thread_dependent_on_time.isAlive():
                brightness_dependent_on_time_mode.set()
                thread_flow = threading.Thread(target=brightness_flow)
                thread_flow.start()
            else:
                brightness_flow_mode.set()
                thread_dependent_on_time = threading.Thread(target=brightness_dependent_on_time)
                thread_dependent_on_time.start()
            time.sleep(WAIT_TIME_AFTER_CLICK)
        elif not GPIO.input(BUTTON_2):
            if current_mode < 5:
                current_mode += 1
            else:
                current_mode = 1
            next_mode.set()
            device.clear()
            time.sleep(WAIT_TIME_AFTER_CLICK)
            next_mode.clear()
        else:
            time.sleep(0.15)


def get_ip():
    return subprocess.run('hostname -I', shell=True, check=True, stdout=subprocess.PIPE).stdout.decode('UTF-8').rstrip()


def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_1, GPIO.IN)
    GPIO.setup(BUTTON_2, GPIO.IN)

    device.show_message_dots(text=get_ip(), delay=1)
    device.write_text(1, "LOADING", dots=[1])

    thread_buttons = threading.Thread(target=button_listener)
    thread_buttons.daemon = True
    thread_buttons.start()

    update_weather()
    update_currency()
    update_instagram()
    device.clear()


modes = {
    1: display_clock,
    2: display_date,
    3: display_weather,
    4: display_currency,
    5: display_instagram
}
current_mode = 1

next_mode = threading.Event()
brightness_flow_mode = threading.Event()
brightness_dependent_on_time_mode = threading.Event()

device = led.sevensegment(cascaded=2)

thread_flow = threading.Thread(target=brightness_flow)
thread_dependent_on_time = threading.Thread(target=brightness_dependent_on_time)
thread_dependent_on_time.start()

init()

if __name__ == '__main__':
    while True:
        modes[current_mode]()
