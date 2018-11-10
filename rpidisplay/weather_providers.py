import logging

import requests

from rpidisplay import configuration


class OpenWeatherMap:
    def __init__(self):
        self._url = 'http://api.openweathermap.org/data/2.5/weather?id={}&units={}&appid={}'
        self._weather_cfg = configuration.WeatherCfg()

    def download_data(self):
        units = {
            'C': 'metric',
            'F': 'imperial'
        }
        unit = units[self._weather_cfg.get_unit().upper()]

        response = requests.get(
            self._url.format(self._weather_cfg.get_location(), unit, self._weather_cfg.get_api_key()))

        status_code = response.status_code
        if status_code / 100 != 2:
            logging.error('Cannot download weather provider=OpenWeatherMap, status code={}', status_code)
            return

        json = response.json()
        return {
            'unit': self._weather_cfg.get_unit().upper(),
            'temp': int(json['main']['temp']),
            'pressure': json['main']['pressure'],
            'humidity': json['main']['humidity']
        }


class DarkSky:
    def __init__(self):
        self._url = 'https://api.darksky.net/forecast/{}/{}/?units={}&exclude=[minutely,hourly,daily,alerts,flags]'
        self._weather_cfg = configuration.WeatherCfg()

    def download_data(self):
        units = {
            'C': 'si',
            'F': 'us'
        }
        unit = units[self._weather_cfg.get_unit().upper()]

        response = requests.get(
            self._url.format(self._weather_cfg.get_api_key(), self._weather_cfg.get_location(), unit))

        status_code = response.status_code
        if status_code / 100 != 2:
            logging.error('Cannot download weather provider=DarkSky, status code={}', status_code)
            return

        json = response.json()

        return {
            'unit': self._weather_cfg.get_unit().upper(),
            'temp': int(json['currently']['temperature']),
            'pressure': int(json['currently']['pressure']),
            'humidity': json['currently']['humidity'] * 100
        }
