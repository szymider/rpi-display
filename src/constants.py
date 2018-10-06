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
WEATHER_API_KEY = 'ec90855c0d358c5f'
'http://api.openweathermap.org/data/2.5/weather?id=3094802&units=metric&appid=ad78b22a5ed247bf2e408004e70749f3'
URL_WEATHER = "https://api.darksky.net/forecast/53c130cb0ba43784f9a50ce6a0dda67f/50.0646501,19.9449799/?exclude=[minutely,hourly,daily,alerts,flags]".format(WEATHER_API_KEY)

# Currency
DISPLAY_RATE_CURRENCY = 2
UPDATE_RATE_CURRENCY = 300
URL_EUR = "http://free.currencyconverterapi.com/api/v5/convert?q=EUR_PLN&compact=y"
URL_USD = "http://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json"

# Instagram followers
DISPLAY_RATE_IG = 5
UPDATE_RATE_IG = 360
IG_USERNAME = 'aredos'
URL_IG = "https://api.instagram.com/v1/users/self/?access_token=".format("378297277.199edf5.309d8ff5741744fbbb1b997f037d3847")

# Dead period of time after clicking a button
WAIT_TIME_AFTER_CLICK = 0.4

# Brightness (hour : brightness)
_HOURS = {
    7: 1,
    11: 2,
    15: 3,
    18: 2,
    24: 1
}
HOURS = OrderedDict(sorted(_HOURS.items(), key=lambda item: item[0]))
