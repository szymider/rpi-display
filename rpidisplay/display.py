from datetime import datetime
from itertools import cycle
from threading import Event

import ZeroSeg.led as led

from rpidisplay import brightness
from rpidisplay import buttons
from rpidisplay import configuration
from rpidisplay import ip


class Display:
    def __init__(self, d):
        self._device = led.Sevensegment(cascaded=2)
        self._modes_cfg = configuration.ModesCfg()
        self._clock_cfg = configuration.ClockCfg()
        self._enabled_modes = self._get_enabled_modes()
        self._data = d
        self._change_mode = Event()
        self._mode = Mode(len(self._enabled_modes), self._change_mode)
        self._brightness = brightness.Brightness(self._device)
        self._buttons = buttons.Buttons(self._mode, self._brightness)
        self._no_data = "NO DATA"

    def start(self):
        if configuration.StartupCfg().get_show_ip():
            self._ip()
        try:
            while True:
                while not self._change_mode.is_set():
                    self._enabled_modes[self._mode.current]()
                self._change_mode.clear()
                self._device.clear()
        except KeyboardInterrupt:
            self._device.clear()
            self._cleanup()

    def _clock(self):
        time = datetime.now().time()
        self._device.write_text(1, " {:%H%M%S}".format(time), dots=(3, 5))
        self._change_mode.wait(self._clock_cfg.get_refresh())

    def _date(self):
        date = datetime.now().date()
        self._device.write_text(1, "{:%d-%m-%y}".format(date))
        self._change_mode.wait(self._modes_cfg.date.get_refresh())

    def _weather(self):
        if self._data.weather:
            self._device.write_text(1, "{:>6d}*{}".format(self._data.weather['temp'], self._data.weather['unit']))
        else:
            self._device.write_text(1, self._no_data)
        self._change_mode.wait(self._modes_cfg.weather.get_refresh())

    def _exchange_rate(self):
        if self._data.exchange_rate:
            for k, v in self._data.exchange_rate.items():
                if not self._change_mode.is_set():
                    self._device.show_message("{} {}".format(v, k), delay=0.2)
        else:
            self._device.write_text(1, self._no_data)
            self._change_mode.wait(1)

    def _instagram(self):
        if self._data.instagram:
            self._device.write_text(1, "IG{:>6d}".format(self._data.instagram['followers']))
        else:
            self._device.write_text(1, self._no_data)
        self._change_mode.wait(self._modes_cfg.instagram.get_refresh())

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
        if self._modes_cfg.instagram.get_enable():
            modes.append(self._instagram)
        return modes

    def _cleanup(self):
        self._buttons.cleanup_gpio()
        self._brightness.cleanup()


class Mode:
    def __init__(self, enabled_modes_amount, change_mode):
        self._cycle = cycle(range(enabled_modes_amount))
        self.current = next(self._cycle)

        self._change_mode = change_mode

    def switch(self):
        self.current = next(self._cycle)
        self._change_mode.set()
