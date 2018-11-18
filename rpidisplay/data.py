import logging
import threading
import time
from collections import OrderedDict

import requests
import schedule

from rpidisplay import configuration
from rpidisplay.weather_providers import OpenWeatherMap, DarkSky


class Data:
    def __init__(self):
        self.weather = None
        self.exchange_rate = None
        self.instagram = None
        self._modes_cfg = configuration.ModesCfg()
        self._weather_provider = self._get_provider()

    def schedule_data_download(self):
        updateable_modes, download_modes = self._get_updateable_modes()
        for mode, enabled in updateable_modes.items():
            if enabled:
                schedule.every(mode.get_update()).seconds.do(download_modes.pop(0))

        if schedule.jobs:
            schedule.run_all()
            threading.Thread(target=self._run_continuously, daemon=True).start()
        else:
            logging.info("No jobs to schedule")

    def _run_continuously(self):
        while True:
            schedule.run_pending()
            time.sleep(2)

    def _get_provider(self):
        if not self._modes_cfg.weather.get_enable():
            return None

        providers = {
            'OWM': OpenWeatherMap,
            'DS': DarkSky,
        }
        config_provider = self._modes_cfg.weather.get_provider().upper()
        provider = providers[config_provider]
        return provider()

    def _get_updateable_modes(self):
        updateable_modes = OrderedDict()
        updateable_modes[self._modes_cfg.weather] = self._modes_cfg.weather.get_enable()
        updateable_modes[self._modes_cfg.exchange_rate] = self._modes_cfg.exchange_rate.get_enable()
        updateable_modes[self._modes_cfg.instagram] = self._modes_cfg.instagram.get_enable()
        return updateable_modes, [self.update_weather, self.update_exchange_rate, self.update_instagram]

    def update_weather(self):
        self.weather = self._weather_provider.download_data()

    def update_exchange_rate(self):
        data = OrderedDict()
        for v in self._modes_cfg.exchange_rate.get_types():
            f = v['from']
            t = v['to']
            response = requests.get('http://free.currencyconverterapi.com/api/v5/convert?q={}_{}&compact=y'.format(
                f.lower(), t.lower()))

            status_code = response.status_code
            if status_code / 100 != 2:
                logging.error('Cannot download exchange rate type={}/{}, status code={} response body={}',
                              f, t, status_code, response.json())
                continue

            json = response.json()

            data['{} {}'.format(f.upper(), t.upper())] = round(json['{}_{}'.format(f.upper(), t.upper())]['val'], 2)
        self.exchange_rate = data

    def update_instagram(self):
        response = requests.get(
            "https://api.instagram.com/v1/users/self/?access_token={}".format(self._modes_cfg.instagram.get_api_key()))

        status_code = response.status_code
        if status_code / 100 != 2:
            logging.error('Cannot download instagram followers, status code={}, response body={}',
                          status_code, response.json())
            return

        json = response.json()
        self.instagram = {
            'followers': json['data']['counts']['followed_by'],
        }
