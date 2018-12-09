# rpi-display 
[![Build Status](https://travis-ci.org/aklimko/rpi-display.svg?branch=master)](https://travis-ci.org/aklimko/rpi-display)
[![Python Version](https://img.shields.io/badge/python-3.5-blue.svg)](#rpi-display)

**rpi-display** shows daily useful info such as current time, date, weather, exchange rates and Instagram followers.
<p align="center">
  <img src="https://raw.githubusercontent.com/exusar/rpi-display/master/preview.gif"/>
</p>

## Table of contents
* [Prerequisites](#Prerequisites)
* [How to use](#How-to-use)
    * [Command line arguments](#Command-line-arguments)
* [Configuration](#Configuration)
    * [Modes](#Modes)
        * [Clock](#Clock)
        * [Date](#Date)
        * [Weather](#Weather)
        * [Exchange rate](#Exchange-rate)
        * [Instagram](#Instagram)
    * [Brightness](#Brightness)
        * [Standard](#Standard)
        * [Time dependent](#Time-dependent)

## Prerequisites
* Raspberry Pi (`0 W` version recommended)
* [ZeroSeg](https://thepihut.com/products/zeroseg) kit

## How to use
This project uses [pipenv](https://pipenv.readthedocs.io) as dependency management  
In case you don't have pipenv installed:
```bash
pip3 install pipenv
```

Run program:
```bash
pipenv run python main.py
```

#### Command line arguments
| Argument |           Description           |  Default |
|:--------:|:-------------------------------:|:--------:|
| -p       | Config location path            | ./config |
| -f       | Config file name (without .yml) | config   |


Running program with these arguments will cause loading config file `./config/my-special-config.yml`:
```bash
pipenv run python main.py -p ./config -f my-special-config
```

## Configuration
### Modes
#### Clock
| Option              | Description                        | Type | Default value |
|---------------------|------------------------------------|------|---------------|
| modes.clock.enable  | Enable clock mode                  | bool | true          |
| modes.clock.refresh | Clock mode refresh rate in seconds | int  | 1             |

#### Date
| Option             | Description                       | Type | Default value |
|--------------------|-----------------------------------|------|---------------|
| modes.date.enable  | Enable mode                       | bool | true          |
| modes.date.refresh | Date mode refresh rate in seconds | int  | 5             |

#### Weather
| Option                 | Description                                                                              | Type | Default value |
|------------------------|------------------------------------------------------------------------------------------|------|---------------|
| modes.weather.enable   | Enable weather mode                                                                      | bool | false         |
| modes.weather.refresh  | Weather mode refresh rate in seconds                                                     | int  | 5             |
| modes.weather.update   | Frequency of downloading new data in seconds                                             | int  | 300           |
| modes.weather.provider | Data provider <br><br>Available options:<br>**OWM** - OpenWeatherMap<br>**DS** - DarkSky | str  |               |
| modes.weather.unit     | Temperature unit <br><br>Available options:<br>**C** - Celsius<br>**F** - Fahrenheit  | str  |               |
| modes.weather.location | Weather station location                                                                 | str  |               |
| modes.weather.api_key  | API key                                                                                  | str  |               |

#### Exchange rate
| Option                      | Description                                  | Type | Default value |
|-----------------------------|----------------------------------------------|------|---------------|
| modes.exchange_rate.enable  | Enable exchange rate mode                    | bool | false         |
| modes.exchange_rate.refresh | Exchange rate mode refresh rate in seconds   | int  | 5             |
| modes.exchange_rate.update  | Frequency of downloading new data in seconds | int  | 300           |
| modes.exchange_rate.types   | Types of exchange rates                      | list |               |

#### Instagram
| Option                  | Description                                  | Type | Default value |
|-------------------------|----------------------------------------------|------|---------------|
| modes.instagram.enable  | Enable exchange rate mode                    | bool | false         |
| modes.instagram.refresh | Exchange rate mode refresh rate in seconds   | int  | 5             |
| modes.instagram.update  | Frequency of downloading new data in seconds | int  | 300           |
| modes.instagram.api_key | API key                                      | str  |               |


### Brightness
| Option          | Description                                                                             | Type | Default value |
|-----------------|-----------------------------------------------------------------------------------------|------|---------------|
| brightness.mode | Active brightness mode <br><br>Available options:<br>**standard**<br>**time_dependent** | str  | standard      |

#### Standard
| Option                                | Description                          | Type | Default value |
|---------------------------------------|--------------------------------------|------|---------------|
| brightness.standard.default           | Default brightness level             | int  | 0             |
| brightness.standard.increase_on_click | Amount of level increase after click | int  | 1             |
| brightness.standard.max               | Max brightness level                 | int  | 15            |

#### Time dependent
| Option                          | Description                                  | Type | Default value |
|---------------------------------|----------------------------------------------|------|---------------|
| brightness.time_dependent.times | Declared list of times and brightness levels | list |               |
