# rpi-display 
[![Build Status](https://travis-ci.org/aklimko/rpi-display.svg?branch=master)](https://travis-ci.org/aklimko/rpi-display)
[![Python Version](https://img.shields.io/badge/python-3.5-blue.svg)](#rpi-display)

**rpi-display** shows daily useful info such as current time, date, weather, exchange rates and Instagram followers.
<p align="center">
  <img src="https://raw.githubusercontent.com/exusar/rpi-display/master/preview.gif"/>
</p>

## Table of Contents
* [Prerequisites](#Prerequisites)
* [How to use](#How-to-use)
    * [Command line arguments](#Command-line-arguments)
* [Configuration](#Configuration)

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
TODO
