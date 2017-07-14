#!/usr/bin/env python
import ZeroSeg.led as led
import RPi.GPIO as GPIO
import time
from datetime import datetime
import urllib, json
import threading

BUTTON_1 = 17
BUTTON_2 = 26

# Weather
REFRESH_RATE_WEATHER = 300
URL_WEATHER = "http://api.wunderground.com/api/DEVKEY/conditions/q/pws:WEATHERSTATION.json"

# Currency
REFRESH_RATE_CURRENCY = 300
URL_EUR = "http://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json"
URL_USD = "http://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json"

# Instagram followers
REFRESH_RATE_IG = 360
URL_IG = "https://www.instagram.com/USERNAME/?__a=1"

WAIT_TIME_AFTER_CLICK = 0.4

def date():
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

def clock():
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
    
def weather():
    print "Weather loading"
    response = urllib.urlopen(URL_WEATHER)
    data = json.loads(response.read())
    weather.temperature = str(int(round(data["current_observation"]["temp_c"], 0)))
    weather.feelslike = str(int(round(float(data["current_observation"]["feelslike_c"]), 0)))
    print "Weather updated"
    
    threading.Timer(REFRESH_RATE_WEATHER, weather).start()

def currency():
    print "Currency loading"
    response_eur = urllib.urlopen(URL_EUR)
    data_eur = json.loads(response_eur.read())
    currency.eur = int(round(data_eur["rates"][0]["mid"], 2) * 100)
    
    response_usd = urllib.urlopen(URL_USD)
    data_usd = json.loads(response_usd.read())
    currency.usd = int(round(data_usd["rates"][0]["mid"], 2) * 100)
    print "Currency updated"
    
    threading.Timer(REFRESH_RATE_CURRENCY, currency).start()
    
def instagram():
    print "Instagram followers loading"
    response = urllib.urlopen(URL_IG)
    data = json.loads(response.read())
    instagram.followers = str(data["user"]["followed_by"]["count"])
    print "Instagram followers updated"
    
    threading.Timer(REFRESH_RATE_IG, instagram).start()

def flow_brightness():
    while not flow_brightness_mode.is_set():
        for intensity in xrange(1, 16, 1):
            device.brightness(intensity)
            flow_brightness_mode.wait(0.1)
        flow_brightness_mode.wait(0.1)
        for intensity in xrange(15, 0, -1):
            device.brightness(intensity)
            flow_brightness_mode.wait(0.1)
        flow_brightness_mode.wait(0.1)
    flow_brightness_mode.clear()
    
def button_listener():
    global mode
    global brightness_level
    global thread_flow
    while True:
        if not GPIO.input(BUTTON_1):
            if brightness_level < 15:
                brightness_level += 2
                device.brightness(brightness_level)
            elif brightness_level == 15 and not thread_flow.is_alive():
                thread_flow.start()
            else:
                flow_brightness_mode.set()
                thread_flow = threading.Thread(target=flow_brightness)
                brightness_level = 1
                device.brightness(brightness_level)
            time.sleep(WAIT_TIME_AFTER_CLICK)
        
        elif not GPIO.input(BUTTON_2):
            if mode < 5:
                mode += 1
            else:
                mode = 1
            next_mode.set()
            device.clear()
            time.sleep(WAIT_TIME_AFTER_CLICK)
            next_mode.clear()
        else:
            time.sleep(0.15)
            pass

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_1, GPIO.IN)
    GPIO.setup(BUTTON_2, GPIO.IN)
    device.brightness(brightness_level)
    device.write_text(1, "LOADING.")
    
    thread_buttons = threading.Thread(target=button_listener)
    thread_buttons.daemon = True
    thread_buttons.start()
    
    weather()
    currency()
    instagram()
    device.clear()

mode = 1    
brightness_level = 1

next_mode = threading.Event()
flow_brightness_mode = threading.Event()

device = led.sevensegment(cascaded=2)

init()

thread_flow = threading.Thread(target=flow_brightness)
    
while True:
    if mode == 1:
        while not next_mode.is_set():
            clock()
            next_mode.wait(1)
        
    elif mode == 2:
        while not next_mode.is_set():
            date()
            next_mode.wait(5)
        
    elif mode == 3:
        while not next_mode.is_set():
            device.write_text(1, weather.temperature + "*C" + weather.feelslike + "*C")
            device.letter(1, 5, 'C', True)
            next_mode.wait(5)
    
    elif mode == 4:
        while not next_mode.is_set():
            device.write_text(1, " " + str(currency.eur) + " EUR")
            device.letter(1, 7, currency.eur / 100, True)
            next_mode.wait(4)
            if not next_mode.is_set():
                device.write_text(1, " " + str(currency.usd) + " USD")
                device.letter(1, 7, currency.usd / 100, True)
                next_mode.wait(4)
        
    elif mode == 5:
        while not next_mode.is_set():
            device.write_text(1, "IG    " + instagram.followers)
            next_mode.wait(5)