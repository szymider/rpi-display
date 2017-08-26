#!/usr/bin/env python
import json
import threading
import time
from urllib import urlopen
from datetime import datetime

import RPi.GPIO as GPIO
import ZeroSeg.led as led

from constants import *


def display_clock():
    while not next_mode.is_set():
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second

        device.letter(1, 7, int(hour / 10))
        device.letter(1, 6, hour % 10, True)
        device.letter(1, 5, int(minute / 10))
        device.letter(1, 4, minute % 10, True)
        device.letter(1, 3, int(second / 10))
        device.letter(1, 2, second % 10)

        next_mode.wait(DISPLAY_RATE_CLOCK)


def display_date():
    while not next_mode.is_set():
        now = datetime.now()
        day = now.day
        month = now.month
        year = now.year - 2000

        device.letter(1, 8, int(day / 10))
        device.letter(1, 7, day % 10)
        device.letter(1, 6, '-')
        device.letter(1, 5, int(month / 10))
        device.letter(1, 4, month % 10)
        device.letter(1, 3, '-')
        device.letter(1, 2, int(year / 10))
        device.letter(1, 1, year % 10)

        next_mode.wait(DISPLAY_RATE_DATE)


def display_weather():
    while not next_mode.is_set():
        device.write_text(1, update_weather.temperature + "*C" + update_weather.feelslike + "*C")
        device.letter(1, 5, 'C', True)

        next_mode.wait(DISPLAY_RATE_WEATHER)


def display_currency():
    while not next_mode.is_set():
        device.write_text(1, " " + str(update_currency.eur) + " EUR")
        device.letter(1, 7, update_currency.eur / 100, True)
        next_mode.wait(DISPLAY_RATE_CURRENCY)
        if not next_mode.is_set():
            device.write_text(1, " " + str(update_currency.usd) + " USD")
            device.letter(1, 7, update_currency.usd / 100, True)
            next_mode.wait(DISPLAY_RATE_CURRENCY)


def display_instagram():
    while not next_mode.is_set():
        device.letter(1, 8, 'I')
        device.letter(1, 7, 'G')

        followers = update_instagram.followers
        j = len(followers) - 1
        for digitPosition in xrange(len(followers)):
            device.letter(1, digitPosition + 1, followers[j])
            j -= 1

        next_mode.wait(DISPLAY_RATE_IG)


def update_weather():
    print "Weather loading"
    response = urlopen(URL_WEATHER)
    data = json.loads(response.read())
    update_weather.temperature = str(int(round(data["current_observation"]["temp_c"], 0)))
    update_weather.feelslike = str(int(round(float(data["current_observation"]["feelslike_c"]), 0)))
    print "Weather updated"

    threading.Timer(UPDATE_RATE_WEATHER, update_weather).start()


def update_currency():
    print "Currency loading"
    response_eur = urlopen(URL_EUR)
    data_eur = json.loads(response_eur.read())
    update_currency.eur = int(round(data_eur["rates"][0]["mid"], 2) * 100)

    response_usd = urlopen(URL_USD)
    data_usd = json.loads(response_usd.read())
    update_currency.usd = int(round(data_usd["rates"][0]["mid"], 2) * 100)
    print "Currency updated"

    threading.Timer(UPDATE_RATE_CURRENCY, update_currency).start()


def update_instagram():
    print "Instagram followers loading"
    response = urlopen(URL_IG)
    data = json.loads(response.read())
    update_instagram.followers = str(data["user"]["followed_by"]["count"])
    print "Instagram followers updated"

    threading.Timer(UPDATE_RATE_IG, update_instagram).start()


def brightness_flow():
    while not brightness_flow_mode.is_set():
        for intensity in xrange(1, 16, 1):
            device.brightness(intensity)
            brightness_flow_mode.wait(0.1)
        brightness_flow_mode.wait(0.1)
        for intensity in xrange(15, 0, -1):
            device.brightness(intensity)
            brightness_flow_mode.wait(0.1)
        brightness_flow_mode.wait(0.1)
    brightness_flow_mode.clear()


def brightness_dependent_on_time():
    while not brightness_dependent_on_time_mode.is_set():
        hour = datetime.now().hour
        if hour <= 7:
            level = 1
        elif hour <= 11:
            level = 3
        elif hour <= 15:
            level = 5
        elif hour <= 18:
            level = 3
        else:
            level = 1
        device.brightness(level)
        brightness_dependent_on_time_mode.wait(300)
    brightness_dependent_on_time_mode.clear()


def button_listener():
    global current_mode
    global thread_flow
    global thread_dependent_on_time
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


def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_1, GPIO.IN)
    GPIO.setup(BUTTON_2, GPIO.IN)

    device.write_text(1, "LOADING.")

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

while True:
    modes[current_mode]()
