from threading import Thread
from datetime import datetime
import events
from display import device
from constants import HOURS


def start_flow():
    global thread_flow
    events.brightness_dependent_on_time_mode.set()
    thread_flow = Thread(target=brightness_flow)
    thread_flow.start()


def start_time_dependent():
    global thread_dependent_on_time
    events.brightness_flow_mode.set()
    thread_dependent_on_time = Thread(target=brightness_dependent_on_time)
    thread_dependent_on_time.start()


def brightness_flow():
    while not events.brightness_flow_mode.is_set():
        for intensity in range(1, 16):
            device.brightness(intensity)
            events.brightness_flow_mode.wait(0.1)
        events.brightness_flow_mode.wait(0.05)
        for intensity in range(15, 0, -1):
            device.brightness(intensity)
            events.brightness_flow_mode.wait(0.1)
        events.brightness_flow_mode.wait(0.05)
    events.brightness_flow_mode.clear()


def brightness_dependent_on_time():
    while not events.brightness_dependent_on_time_mode.is_set():
        hour = datetime.now().hour
        for hour_threshold in HOURS.keys():
            if hour <= hour_threshold:
                device.brightness(HOURS[hour_threshold])
                break
        events.brightness_dependent_on_time_mode.wait(300)
    events.brightness_dependent_on_time_mode.clear()


thread_flow = Thread(target=brightness_flow)
thread_dependent_on_time = Thread(target=brightness_dependent_on_time)
