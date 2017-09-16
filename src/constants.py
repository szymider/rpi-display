from collections import OrderedDict

# Buttons GPIO pins
BUTTON_1 = 17
BUTTON_2 = 26

# Clock (slightly lower than a second to avoid skipping a second once in a while)
DISPLAY_RATE_CLOCK = 0.995

# Date
DISPLAY_RATE_DATE = 5

# Weather
DISPLAY_RATE_WEATHER = 5
UPDATE_RATE_WEATHER = 300
URL_WEATHER = "http://api.wunderground.com/api/ec90855c0d358c5f/conditions/q/pws:IKRAKW27.json"

# Currency
DISPLAY_RATE_CURRENCY = 3
UPDATE_RATE_CURRENCY = 300
URL_EUR = "http://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json"
URL_USD = "http://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json"

# Instagram followers
DISPLAY_RATE_IG = 5
UPDATE_RATE_IG = 360
URL_IG = "https://www.instagram.com/aredos/?__a=1"

# Dead period of time after clicking a button
WAIT_TIME_AFTER_CLICK = 0.4

# Brightness (hour : brightness)
HOURS = {
    7: 1,
    11: 3,
    15: 5,
    18: 3,
    24: 1
}
HOURS = OrderedDict(sorted(HOURS.items(), key=lambda item: item[0]))
