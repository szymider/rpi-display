import threading
import time
import requests
import subprocess
from datetime import datetime
from itertools import cycle

import RPi.GPIO as GPIO
import ZeroSeg.led as led

import update
import ip
import messages
from constants import *


def display_clock():
    now = datetime.now()
    device.write_text(1, " {:%H%M%S}".format(now.time()), dots=(3, 5))
    next_mode.wait(DISPLAY_RATE_CLOCK)


def display_date():
    now = datetime.now()
    device.write_text(1, "{:%d-%m-%y}".format(now.date()))
    next_mode.wait(DISPLAY_RATE_DATE)


# FIXME: case when temp is negative double digit
def display_weather():
    device.write_text(1, "{:2d}*C{:2d}*C".format(update.temperature, update.feelslike), dots=[4])
    next_mode.wait(DISPLAY_RATE_WEATHER)


def display_currency():
    device.write_text(1, " {:d} EUR".format(update.eur), dots=[6])
    next_mode.wait(DISPLAY_RATE_CURRENCY)
    if not next_mode.is_set():
        device.write_text(1, " {:d} USD".format(update.usd), dots=[6])
        next_mode.wait(DISPLAY_RATE_CURRENCY)


def display_instagram():
    device.write_text(1, "IG{:>6d}".format(update.followers))
    next_mode.wait(DISPLAY_RATE_IG)


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


def start_flow():
    global thread_flow
    brightness_dependent_on_time_mode.set()
    thread_flow = threading.Thread(target=brightness_flow)
    thread_flow.start()


def start_time_dependent():
    global thread_dependent_on_time
    brightness_flow_mode.set()
    thread_dependent_on_time = threading.Thread(target=brightness_dependent_on_time)
    thread_dependent_on_time.start()


def wait_for_message_display():
    time.sleep(0.2)


def button_listener():
    global current_mode
    global thread_flow, thread_dependent_on_time
    while True:
        if GPIO.event_detected(BUTTON_1):
            if messages.messages_to_read:
                message = messages.messages_to_read.popleft()
                show_message(message)
                messages.send_read_id(message['id'])
            else:
                show_message(None)
            time.sleep(WAIT_TIME_AFTER_CLICK)
        elif GPIO.event_detected(BUTTON_2):
            current_mode = next(mode)
            next_mode.set()
            device.clear()
            time.sleep(WAIT_TIME_AFTER_CLICK)
        else:
            time.sleep(0.2)


def show_message(message=None):
    global current_mode
    device.clear()
    remember_mode, current_mode = current_mode, 0
    if message:
        device.show_message(text=message['text'].upper(), mw=True)
    else:
        device.write_text(1, "NO MSGS", mw=True)
        time.sleep(2)
    current_mode = remember_mode


def setup_button_listener():
    threading.Thread(target=button_listener, daemon=True).start()


def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_1, GPIO.IN)
    GPIO.setup(BUTTON_2, GPIO.IN)
    GPIO.add_event_detect(BUTTON_1, GPIO.RISING, bouncetime=250)
    GPIO.add_event_detect(BUTTON_2, GPIO.RISING, bouncetime=250)

    device.show_message(text=ip.ip)
    device.write_text(1, "LOADING", dots=[1])

    setup_button_listener()
    update.all_modes()
    messages.setup_messages_service()
    ip.send_ip()
    device.clear()


modes = {
    0: wait_for_message_display,
    1: display_clock,
    2: display_date,
    3: display_weather,
    4: display_currency,
    5: display_instagram
}
current_mode = 1
mode = cycle(range(1, 6))
next(mode)

next_mode = threading.Event()
brightness_flow_mode = threading.Event()
brightness_dependent_on_time_mode = threading.Event()

device = led.sevensegment(cascaded=2)

thread_flow = threading.Thread(target=brightness_flow)
thread_dependent_on_time = threading.Thread(target=brightness_dependent_on_time)
thread_dependent_on_time.start()

if __name__ == '__main__':
    init()
    while True:
        while not next_mode.is_set():
            modes[current_mode]()
        next_mode.clear()
