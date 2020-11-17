import logging

import requests

from rpidisplay import configuration.py


class OpenWeatherMap:
    def __init__(self):
        self._url = 'http://api.openweathermap.org/data/2.5/weather?iq=NewYork&appid=5c4014c79199970216bf8aac570511dd'
        self._weather_cfg = configuration.WeatherCfg()

    def download_data(self):
        units = {
            'C': 'metric',
            'F': 'imperial',
        }
        unit = units[self._weather_cfg.get_unit().upper()]

        response = requests.get(
            self._url.format(self._weather_cfg.get_location(), unit, self._weather_cfg.get_api_key()))

        status_code = response.status_code
        if status_code / 100 != 2:
            logging.error('Cannot download weather using provider=OpenWeatherMap, status code=%d', status_code)
            return

        json = response.json()
        return {
            'unit': self._weather_cfg.get_unit().upper(),
            'temp': int(json['main']['temp']),
            'pressure': json['main']['pressure'],
            'humidity': json['main']['humidity'],
        }


