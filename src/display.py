from datetime import datetime
from threading import Event

import RPi.GPIO as GPIO
import ZeroSeg.led as led

import configuration
import data
import ip


class Display:
    def __init__(self, data: data.Data, change_mode: Event):
        self.button_left = 17
        self.button_right = 26
        self._setup_gpio()
        self._device = led.Sevensegment(cascaded=2)
        self._mode = configuration.ModeCfg()
        self._clock = configuration.ClockCfg()
        self._data = data
        self._change_mode = change_mode

    def clock(self):
        time = datetime.now().time()
        self._device.write_text(1, " {:%H%M%S}".format(time), dots=(3, 5))
        self._change_mode.wait(self._clock.get_refresh())

    def date(self):
        date = datetime.now().date()
        self._device.write_text(1, "{:%d-%m-%y}".format(date))
        self._change_mode.wait(self._mode.date.get_refresh())

    def weather(self):
        self._device.write_text(1, "{:>6d}*C".format(self._data.weather))
        self._change_mode.wait(self._mode.weather.get_refresh())

    def exchange_rate(self):
        for k, v in self._data.exchange_rate:
            if not self._change_mode.is_set():
                self._device.show_message(" {:d} {}".format(v, k), delay=0.2)
                self._change_mode.wait(self._mode.exchange_rate.get_refresh())

    def instagram(self):
        self._device.write_text(1, "IG{:>6d}".format(self._data.ig))
        self._change_mode.wait(self._mode.ig.get_refresh())

    def config_changed(self):
        self._device.show_message("CONFIG CHANGED", delay=0.1)

    def ip(self):
        self._device.show_message(text=ip.get_ip())

    def _setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_left, GPIO.IN)
        GPIO.setup(self.button_right, GPIO.IN)
        GPIO.add_event_detect(self.button_left, GPIO.RISING, bouncetime=250)
        GPIO.add_event_detect(self.button_right, GPIO.RISING, bouncetime=250)
