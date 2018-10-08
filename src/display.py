from datetime import datetime
from itertools import cycle

import ZeroSeg.led as led

import buttons
import configuration
import ip


class Display:
    def __init__(self, d, change_mode):
        self._device = led.Sevensegment(cascaded=2)
        self._modes_cfg = configuration.ModesCfg()
        self._clock_cfg = configuration.ClockCfg()
        self._enabled_modes = self._get_enabled_modes()
        self._data = d
        self._change_mode = change_mode
        self._mode = Mode(len(self._enabled_modes), self._change_mode)
        self.buttons = buttons.Buttons(self._mode)

    def start(self):
        self._device.brightness(1)
        if configuration.StartupCfg().get_show_ip():
            self._ip()

        while True:
            while not self._change_mode.is_set():
                self._enabled_modes[self._mode.current]()
            self._change_mode.clear()
            self._device.clear()

    def _clock(self):
        time = datetime.now().time()
        self._device.write_text(1, " {:%H%M%S}".format(time), dots=(3, 5))
        self._change_mode.wait(self._clock_cfg.get_refresh())

    def _date(self):
        date = datetime.now().date()
        self._device.write_text(1, "{:%d-%m-%y}".format(date))
        self._change_mode.wait(self._modes_cfg.date.get_refresh())

    def _weather(self):
        self._device.write_text(1, "{:>6d}*{}".format(self._data.weather['temp'], self._data.weather['unit']))
        self._change_mode.wait(self._modes_cfg.weather.get_refresh())

    def _exchange_rate(self):
        for k, v in self._data.exchange_rate.items():
            if not self._change_mode.is_set():
                self._device.show_message("{} {}".format(v, k), delay=0.2)

    def _instagram(self):
        self._device.write_text(1, "IG{:>6d}".format(self._data.ig['followers']))
        self._change_mode.wait(self._modes_cfg.ig.get_refresh())

    def config_changed(self):
        self._device.show_message("CONFIG CHANGED", delay=0.1)

    def _ip(self):
        self._device.show_message(text=ip.get_ip())

    def _get_enabled_modes(self):
        modes = []
        if self._modes_cfg.clock.get_enable():
            modes.append(self._clock)
        if self._modes_cfg.date.get_enable():
            modes.append(self._date)
        if self._modes_cfg.weather.get_enable():
            modes.append(self._weather)
        if self._modes_cfg.exchange_rate.get_enable():
            modes.append(self._exchange_rate)
        if self._modes_cfg.ig.get_enable():
            modes.append(self._instagram)
        return modes


class Mode:
    def __init__(self, enabled_modes_amount, change_mode):
        self.cycle = cycle(range(enabled_modes_amount))
        self.current = next(self.cycle)

        self._change_mode = change_mode

    def switch(self):
        self.current = next(self.cycle)
        self._change_mode.set()
