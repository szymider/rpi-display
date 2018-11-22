import logging
import sys

from rpidisplay import configuration


class Brightness:
    def __init__(self, device):
        self._device = device
        self._cfg = configuration.BrightnessCfg()
        self._mode = self._get_mode()

    def _get_mode(self):
        mode = None
        cfg_default_mode = self._cfg.get_default_mode()
        if cfg_default_mode == 'standard':
            mode = Standard(self._device)
        elif cfg_default_mode == 'time_dependent':
            mode = TimeDependent(self._device)
        else:
            logging.error("Invalid brightness mode=%s", cfg_default_mode)
            sys.exit(1)
        return mode

    def on_click(self):
        self._mode.on_click()


class Standard:
    def __init__(self, device):
        self._device = device
        self._cfg = configuration.BrightnessCfg().standard
        self._default = self._cfg.get_default()
        self._increase_on_click = self._cfg.get_increase_on_click()
        self._max = self._cfg.get_max()
        self._level = self._default
        self._device.brightness(self._level)

    def on_click(self):
        self._change_level()
        self._set_brightness()

    def _change_level(self):
        print(self._level)
        level_after_increase = self._level + self._increase_on_click
        self._level = level_after_increase if level_after_increase <= self._max else 1

    def _set_brightness(self):
        self._device.brightness(self._level)


class TimeDependent:
    def __init__(self, device):
        self._device = device
        self._cfg = configuration.BrightnessCfg().time_dependent
        self._hours = self._cfg.get_hours()

    def on_click(self):
        pass
