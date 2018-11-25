import logging
from collections import OrderedDict

import requests
from apscheduler.schedulers.background import BackgroundScheduler

from rpidisplay import configuration
from rpidisplay.weather_providers import OpenWeatherMap, DarkSky


class Data:
    def __init__(self):
        self.weather = None
        self.exchange_rate = None
        self.instagram = None
        self._modes_cfg = configuration.ModesCfg()
        self._weather_provider = self._get_provider()
        self._scheduler = BackgroundScheduler()

    def schedule_data_download(self):
        updateable_modes, download_modes = self._get_updateable_modes()
        for mode, enabled in updateable_modes.items():
            if enabled:
                update_job = download_modes.pop(0)
                update_job()
                self._scheduler.add_job(update_job, trigger='interval', seconds=mode.get_update())

        if self._scheduler.get_jobs():
            self._scheduler.start()
        else:
            logging.info("No jobs to schedule")

    def cleanup(self):
        if self._scheduler.state:
            self._scheduler.shutdown(wait=False)
            logging.info('Data scheduler has been shutdown')

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
                f, t))

            status_code = response.status_code
            if status_code / 100 != 2:
                logging.error('Cannot download exchange rate type=%s/%s, status code=%d response body=%s',
                              f, t, status_code, response.json())
                continue

            json = response.json()
            if not json:
                logging.error('Failed to download exchange rate type=%s/%s', f, t)
                continue

            data['{} {}'.format(f.upper(), t.upper())] = round(json['{}_{}'.format(f.upper(), t.upper())]['val'], 2)
        self.exchange_rate = data

    def update_instagram(self):
        response = requests.get(
            "https://api.instagram.com/v1/users/self/?access_token={}".format(self._modes_cfg.instagram.get_api_key()))

        status_code = response.status_code
        if status_code / 100 != 2:
            logging.error('Cannot download instagram followers, status code=%d, response body=%s',
                          status_code, response.json())
            return

        json = response.json()
        self.instagram = {
            'followers': json['data']['counts']['followed_by'],
        }
