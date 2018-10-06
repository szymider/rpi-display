import threading
import time
from itertools import cycle

import RPi.GPIO as GPIO

import events
import threads
import update
from constants import *


def hide_display():
    events.change_mode.wait(5)


def wait_for_message_display():
    time.sleep(0.2)


def button_listener():
    global current_mode
    while True:
        if GPIO.event_detected(BUTTON_1):
            # if messages.messages_to_read:
            #     message = messages.messages_to_read.popleft()
            #     threads.start_time_dependent()
            #     show_message(message)
            #     if messages.messages_to_read:
            #         threads.start_flow()
            #     messages.send_read_id(message['id'])
            # else:
            #     show_message()
            time.sleep(WAIT_TIME_AFTER_CLICK)
        elif GPIO.event_detected(BUTTON_2):
            current_mode = next(mode)
            events.change_mode.set()
            device.clear()
            time.sleep(WAIT_TIME_AFTER_CLICK)
        else:
            time.sleep(0.2)


def setup_button_listener():
    threading.Thread(target=button_listener, daemon=True).start()


def init():
    threads.thread_dependent_on_time.start()

    setup_button_listener()
    update.all_modes()
    device.clear()


current_mode = 1
mode = cycle(range(6))
next(mode)

if __name__ == '__main__':
    init()
    while True:
        while not events.change_mode.is_set():
            modes[current_mode]()
        events.change_mode.clear()
