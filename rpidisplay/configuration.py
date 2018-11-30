import logging
import sys

from jsonschema import validate, ValidationError
from vyper import v


def setup_logging():
    logging.basicConfig(format='%(asctime)s [%(module)s] |%(levelname)s| %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S',
                        level=logging.INFO)


def setup_config(path, file_name):
    _setup_defaults()
    _setup_file(path, file_name)


def _setup_defaults():
    v.set_default('modes.clock.enable', True)
    v.set_default('modes.clock.refresh', 0.995)

    v.set_default('modes.date.enable', True)
    v.set_default('modes.date.refresh', 5)

    v.set_default('modes.weather.enable', False)
    v.set_default('modes.weather.refresh', 5)
    v.set_default('modes.weather.update', 300)

    v.set_default('modes.exchange_rate.enable', False)
    v.set_default('modes.exchange_rate.update', 300)

    v.set_default('modes.instagram.enable', False)
    v.set_default('modes.instagram.refresh', 5)
    v.set_default('modes.instagram.update', 360)

    v.set_default('brightness.mode', 'standard')
    v.set_default('brightness.standard.default', 0)
    v.set_default('brightness.standard.increase_on_click', 3)
    v.set_default('brightness.standard.max', 15)


def _setup_file(path, name):
    v.add_config_path(path)
    v.set_config_name(name)
    v.set_config_type('yaml')

    try:
        v.read_in_config()
    except FileNotFoundError:
        logging.info("Config file was not found")
    except OSError as e:
        logging.warning(e)


def validate_config():
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Config schema",
        "definitions": {
            "brightness_level": {"type": "number", "multipleOf": 1.0, "minimum": 0, "maximum": 15},
            "not_empty_string": {"type": "string", "minLength": 1}
        },
        "type": "object",
        "properties": {
            "modes": {
                "type": "object",
                "properties": {
                    "clock": {
                        "type": "object",
                        "properties": {
                            "enable": {"type": "boolean"}
                        },
                        "if": {
                            "properties": {
                                "enable": {"enum": [True]}
                            }
                        },
                        "then": {
                            "properties": {
                                "refresh": {"type": "number"}
                            },
                            "required": ["refresh"]
                        }
                    },
                    "date": {
                        "type": "object",
                        "properties": {
                            "enable": {"type": "boolean"}
                        },
                        "if": {
                            "properties": {
                                "enable": {"enum": [True]}
                            }
                        },
                        "then": {
                            "properties": {
                                "refresh": {"type": "number"}
                            }
                        }
                    },
                    "weather": {
                        "type": "object",
                        "properties": {
                            "enable": {"type": "boolean"}
                        },
                        "if": {
                            "properties": {
                                "enable": {"enum": [True]}
                            }
                        },
                        "then": {
                            "properties": {
                                "refresh": {"type": "number"},
                                "update": {"type": "number"},
                                "provider": {"type": "string", "enum": ['OWM', 'owm', 'DS', 'ds']},
                                "unit": {"type": "string", "enum": ['C', 'c', 'F', 'f']},
                                "location": {"$ref": "#/definitions/not_empty_string"},
                                "api_key": {"$ref": "#/definitions/not_empty_string"}
                            },
                            "required": ["refresh", "update", "provider", "unit", "location", "api_key"]
                        }
                    },
                    "exchange_rate": {
                        "type": "object",
                        "properties": {
                            "enable": {"type": "boolean"}
                        },
                        "if": {
                            "properties": {
                                "enable": {"enum": [True]}
                            }
                        },
                        "then": {
                            "properties": {
                                "refresh": {"type": "number"},
                                "update": {"type": "number"},
                                "types": {
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "from": {"$ref": "#/definitions/not_empty_string"},
                                            "to": {"$ref": "#/definitions/not_empty_string"}
                                        },
                                        "required": ["from", "to"]
                                    }
                                }
                            },
                            "required": ["refresh", "update", "types"]
                        }
                    },
                    "instagram": {
                        "type": "object",
                        "properties": {
                            "enable": {"type": "boolean"}
                        },
                        "if": {
                            "properties": {
                                "enable": {"enum": [True]}
                            }
                        },
                        "then": {
                            "properties": {
                                "refresh": {"type": "number"},
                                "update": {"type": "number"},
                                "api_key": {"$ref": "#/definitions/not_empty_string"}
                            },
                            "required": ["refresh", "update", "api_key"]
                        }
                    }
                }
            },
            "brightness": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["standard", "time_dependent"]}
                },
                "if": {
                    "properties": {
                        "mode": {"enum": ['standard']}
                    }
                },
                "then": {
                    "properties": {
                        "standard": {
                            "type": "object",
                            "properties": {
                                "default": {"$ref": "#/definitions/brightness_level"},
                                "increase_on_click": {"type": "number", "multipleOf": 1.0, "minimum": 1,
                                                      "maximum": 15},
                                "max": {"$ref": "#/definitions/brightness_level"}
                            },
                            "required": ["default", "increase_on_click", "max"]
                        },
                    },
                    "required": ["standard"]
                },
                "else": {
                    "properties": {
                        "time_dependent": {
                            "type": "object",
                            "properties": {
                                "times": {
                                    "type": "array",
                                    "minItems": 2,
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "from": {"type": "string", "pattern": "^([0-1][0-9]|[2][0-3]):[0-5][0-9]$"},
                                            "value": {"$ref": "#/definitions/brightness_level"}
                                        },
                                        "required": ["from", "value"]
                                    }
                                }
                            },
                            "required": ["times"]
                        }
                    },
                    "required": ["time_dependent"]
                }
            }
        }
    }

    try:
        validate(v.all_settings(), schema)
    except ValidationError as e:
        logging.error(".".join(x for x in e.path if isinstance(x, str)) + ": " + e.message)
        sys.exit(0)


class ModesCfg:
    def __init__(self):
        self.clock = ClockCfg()
        self.date = DateCfg()
        self.weather = WeatherCfg()
        self.exchange_rate = ExchangeRateCfg()
        self.instagram = InstagramCfg()


class ClockCfg:
    def __init__(self):
        self._v = v

    def get_enable(self):
        return self._v.get_bool('modes.clock.enable')

    def get_refresh(self):
        return self._v.get_float('modes.clock.refresh')


class DateCfg:
    def __init__(self):
        self._v = v

    def get_enable(self):
        return self._v.get_bool('modes.date.enable')

    def get_refresh(self):
        return self._v.get_float('modes.date.refresh')


class WeatherCfg:
    def __init__(self):
        self._v = v

    def get_enable(self):
        return self._v.get_bool('modes.weather.enable')

    def get_refresh(self):
        return self._v.get_float('modes.weather.refresh')

    def get_update(self):
        return self._v.get_float('modes.weather.update')

    def get_provider(self):
        return self._v.get_string('modes.weather.provider')

    def get_unit(self):
        return self._v.get_string('modes.weather.unit')

    def get_location(self):
        return self._v.get_string('modes.weather.location')

    def get_api_key(self):
        return self._v.get_string('modes.weather.api_key')


class ExchangeRateCfg:
    def __init__(self):
        self._v = v

    def get_enable(self):
        return self._v.get_bool('modes.exchange_rate.enable')

    def get_update(self):
        return self._v.get_float('modes.exchange_rate.update')

    def get_types(self):
        return self._v.get('modes.exchange_rate.types')


class InstagramCfg:
    def __init__(self):
        self._v = v

    def get_enable(self):
        return self._v.get_bool('modes.instagram.enable')

    def get_refresh(self):
        return self._v.get_float('modes.instagram.refresh')

    def get_update(self):
        return self._v.get_float('modes.instagram.update')

    def get_api_key(self):
        return self._v.get_string('modes.instagram.api_key')


class BrightnessCfg:
    def __init__(self):
        self._v = v
        self.standard = StandardCfg()
        self.time_dependent = TimeDependentCfg()

    def get_mode(self):
        return self._v.get_string('brightness.mode')


class StandardCfg:
    def __init__(self):
        self._v = v

    def get_default(self):
        return self._v.get_int('brightness.standard.default')

    def get_increase_on_click(self):
        return self._v.get_int('brightness.standard.increase_on_click')

    def get_max(self):
        return self._v.get_int('brightness.standard.max')


class TimeDependentCfg:
    def __init__(self):
        self._v = v

    def get_times(self):
        return self._v.get('brightness.time_dependent.times')
