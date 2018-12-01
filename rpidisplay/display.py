from itertools import cycle
from threading import Event

import ZeroSeg.led as led

from rpidisplay import brightness
from rpidisplay import buttons
from rpidisplay import configuration
from rpidisplay import datetime_provider


class Display:
    def __init__(self, d):
        self._change_mode_event = Event()
        self._display_responsive_event = Event()
        self._device = led.Sevensegment(cascaded=2, responsive_event=self._display_responsive_event)
        self._modes_cfg = configuration.ModesCfg()
        self._clock_cfg = configuration.ClockCfg()
        self._enabled_modes = self._get_enabled_modes()
        self._data = d
        self._mode = Mode(len(self._enabled_modes), self._change_mode_event)
        self._brightness = brightness.Brightness(self._device)
        self._buttons = buttons.Buttons(self._mode, self._brightness, self._display_responsive_event)
        self._no_data_text = "NO DATA"

    def start(self):
        self._brightness.start()
        self._buttons.setup_gpio()

        try:
            while True:
                while not self._change_mode_event.is_set():
                    self._enabled_modes[self._mode.current]()
                self._change_mode_event.clear()
                self._display_responsive_event.clear()
                self._device.clear()
        except KeyboardInterrupt:
            self._device.clear()
            self._cleanup()

    def _clock(self):
        time = datetime_provider.get_current_time()
        self._device.write_text(1, " {:%H%M%S}".format(time), dots=(3, 5))
        self._change_mode_event.wait(self._clock_cfg.get_refresh())

    def _date(self):
        date = datetime_provider.get_current_date()
        self._device.write_text(1, "{:%d-%m-%y}".format(date))
        self._change_mode_event.wait(self._modes_cfg.date.get_refresh())

    def _weather(self):
        if self._data.weather:
            self._device.write_text(1, "{:>6d}*{}".format(self._data.weather['temp'], self._data.weather['unit']))
        else:
            self._device.write_text(1, self._no_data_text)
        self._change_mode_event.wait(self._modes_cfg.weather.get_refresh())

    def _exchange_rate(self):
        if self._data.exchange_rate:
            for k, v in self._data.exchange_rate.items():
                if not self._change_mode_event.is_set():
                    self._device.show_message("{} {}".format(v, k), delay=0.2)
        else:
            self._device.write_text(1, self._no_data_text)
            self._change_mode_event.wait(1)

    def _instagram(self):
        if self._data.instagram:
            self._device.write_text(1, "IG{:>6d}".format(self._data.instagram['followers']))
        else:
            self._device.write_text(1, self._no_data_text)
        self._change_mode_event.wait(self._modes_cfg.instagram.get_refresh())

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
        self._data.cleanup()


class Mode:
    def __init__(self, enabled_modes_amount, change_mode_event):
        self._cycle = cycle(range(enabled_modes_amount))
        self.current = next(self._cycle)

        self._change_mode_event = change_mode_event

    def switch(self):
        self.current = next(self._cycle)
        self._change_mode_event.set()
