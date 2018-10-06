import logging
import sys

from vyper import v, FlagsProvider


def setup_logging():
    logging.basicConfig(format='%(asctime)s [%(module)s] |%(levelname)s| %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S',
                        level=logging.INFO)


def setup_config():
    _setup_defaults()
    _setup_arguments()
    _setup_file()
    _validate_config()


def _setup_defaults():
    v.set_default('startup.show_ip', True)

    v.set_default('mode.clock.enable', True)
    v.set_default('mode.clock.refresh', 0.995)

    v.set_default('mode.date.enable', True)
    v.set_default('mode.date.refresh', 5)

    v.set_default('mode.weather.enable', False)
    v.set_default('mode.weather.refresh', 5)
    v.set_default('mode.weather.update', 300)

    v.set_default('mode.exchange_rate.enable', False)
    v.set_default('mode.exchange_rate.refresh', 5)
    v.set_default('mode.exchange_rate.update', 300)

    v.set_default('mode.ig.enable', False)
    v.set_default('mode.ig.refresh', 5)
    v.set_default('mode.ig.update', 360)

    v.set_default('buttons.wait_time_after_click', 0.4)

    v.set_default('brightness.default_mode', 'standard')
    v.set_default('brightness.standard.default', 1)
    v.set_default('brightness.standard.increase_on_click', 2)


def _setup_arguments():
    _setup_default_arguments()

    fp = FlagsProvider()
    fp.add_argument('-cp', type=str, help='Configs location path')
    fp.add_argument('-cf', type=str, help='Config file name (without .yml extension)')
    v.bind_flags(fp, sys.argv)


def _setup_default_arguments():
    v.set_default('cp', './config')
    v.set_default('cf', 'config')


def _setup_file():
    v.set_config_name(v.get_string('cf'))
    v.set_config_type('yaml')
    v.add_config_path(v.get_string('cp'))
    v.read_in_config()

    v.on_config_change(_config_changed)
    v.watch_config()


def _validate_config():
    # TODO
    pass


def _config_changed():
    logging.info("Detected config file change. Config reloaded.")


class StartupCfg:
    def __init__(self):
        self.v = v

    def get_show_ip(self):
        return self.v.get_bool('startup.show_ip')


class ModeCfg:
    def __init__(self):
        self.clock: ClockCfg = ClockCfg()
        self.date: DateCfg = DateCfg()
        self.weather: WeatherCfg = WeatherCfg()
        self.exchange_rate: ExchangeRateCfg = ExchangeRateCfg()
        self.ig: IgCfg = IgCfg()


class ClockCfg:
    def __init__(self):
        self._v = v

    def get_enable(self):
        return self._v.get_bool('mode.clock.enable')

    def get_refresh(self):
        return self._v.get_float('mode.clock.refresh')


class DateCfg:
    def __init__(self):
        self._v = v

    def get_enable(self):
        return self._v.get_bool('mode.date.enable')

    def get_refresh(self):
        return self._v.get_float('mode.date.refresh')


class WeatherCfg(object):
    def __init__(self):
        self._v = v

    def get_enable(self):
        return self._v.get_bool('mode.weather.enable')

    def get_refresh(self):
        return self._v.get_float('mode.weather.refresh')

    def get_update(self):
        return self._v.get_float('mode.weather.update')

    def get_provider(self):
        return self._v.get_string('mode.weather.provider')

    def get_unit(self):
        return self._v.get_string('mode.weather.unit')

    def get_location(self):
        return self._v.get_string('mode.weather.location')

    def get_api_key(self):
        return self._v.get_string('mode.weather.api_key')


class ExchangeRateCfg:
    def __init__(self):
        self._v = v

    def get_enable(self):
        return self._v.get_bool('mode.exchange_rate.enable')

    def get_refresh(self):
        return self._v.get_float('mode.exchange_rate.refresh')

    def get_update(self):
        return self._v.get_float('mode.exchange_rate.update')

    def get_types(self):
        return self._v.get('mode.exchange_rate.types')


class IgCfg:
    def __init__(self):
        self._v = v

    def get_enable(self):
        return self._v.get_bool('mode.ig.enable')

    def get_refresh(self):
        return self._v.get_float('mode.ig.refresh')

    def get_update(self):
        return self._v.get_float('mode.ig.update')

    def get_api_key(self):
        return self._v.get_string('mode.ig.api_key')


class ButtonsCfg:
    def __init__(self):
        self._v = v

    def get_wait_time_after_click(self):
        return self._v.get_float('buttons.wait_time_after_click')


class BrightnessCfg:
    def __init__(self):
        self._v = v
        self.standard: StandardCfg = StandardCfg()
        self.time_dependent: TimeDependentCfg = TimeDependentCfg()

    def get_default_mode(self):
        return self._v.get_string('brightness.default_mode')


class StandardCfg:
    def __init__(self):
        self._v = v

    def get_default_value(self):
        return self._v.get_int('brightness.standard.default_value')

    def get_increase_on_click(self):
        return self._v.get_int('brightness.standard.increase_on_click')


class TimeDependentCfg:
    def __init__(self):
        self._v = v

    def get_hours(self):
        return self._v.get('brightness.time_dependent.hours')
