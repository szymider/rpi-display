import datetime
import logging
import sys
import threading
import time

import schedule

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
        level_after_increase = self._level + self._increase_on_click
        self._level = level_after_increase if level_after_increase <= self._max else 1

    def _set_brightness(self):
        self._device.brightness(self._level)


class TimeDependent:
    def __init__(self, device):
        self._device = device
        self._cfg = configuration.BrightnessCfg().time_dependent
        self._times = self._convert_times()
        self._level = None
        self._watch_times()
        self._scheduler = schedule.Scheduler()
        self._watcher = threading.Thread(target=self._run_scheduler, daemon=True).start()

    def _convert_times(self):
        time_format = '%H:%M'
        times = sorted(self._cfg.get_hours(), key=lambda x: time.strptime(x['from'], time_format), reverse=True)
        for t in times:
            t['from'] = time.strptime(t['from'], time_format)
        return times

    def _run_scheduler(self):
        now_seconds = datetime.datetime.now().second
        time.sleep(60 - now_seconds)

        self._scheduler.every().minute.do(self._watch_times)
        self._watch_times()

        while True:
            self._scheduler.run_pending()
            time.sleep(1)

    def _watch_times(self):
        now = datetime.datetime.now().time()
        for t in self._times:
            tf = t['from']
            if now >= datetime.time(hour=tf.tm_hour, minute=tf.tm_min):
                value = t['value']
                if self._level != value:
                    self._device.brightness(value)
                    self._level = value
                break

    def on_click(self):
        pass
