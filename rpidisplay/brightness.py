import datetime
import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler

from rpidisplay import configuration


class Brightness:
    def __init__(self, device):
        self._device = device
        self._cfg = configuration.BrightnessCfg()
        self._mode = self._get_mode()

    def _get_mode(self):
        modes = {
            'standard': Standard,
            'time_dependent': TimeDependent,
        }
        return modes[self._cfg.get_mode()](self._device)

    def on_click(self):
        self._mode.on_click()

    def cleanup(self):
        self._mode.cleanup()


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

    def cleanup(self):
        pass

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
        self._scheduler = self._setup_scheduler()

    def on_click(self):
        pass

    def cleanup(self):
        self._scheduler.shutdown()
        logging.info('Shutdown scheduler')

    def _setup_scheduler(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self._watch_times, trigger='cron', minute='*/1')
        scheduler.start()
        return scheduler

    def _convert_times(self):
        time_format = '%H:%M'
        times = sorted(self._cfg.get_times(), key=lambda x: time.strptime(x['from'], time_format), reverse=True)
        for t in times:
            t['from'] = time.strptime(t['from'], time_format)
        return times

    def _watch_times(self):
        now = datetime.datetime.now().time()
        for t in self._times:
            tf = t['from']
            if now >= datetime.time(hour=tf.tm_hour, minute=tf.tm_min):
                value = t['value']
                if self._level != value:
                    self._set_brightness(value)
                return
        latest_value = self._times[0]['value']
        self._set_brightness(latest_value)

    def _set_brightness(self, value):
        self._device.brightness(value)
        self._level = value
