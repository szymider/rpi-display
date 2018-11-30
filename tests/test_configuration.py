import pytest
from jsonschema import ValidationError

from rpidisplay import configuration


@pytest.fixture
def load_config():
    configuration.setup_config('./tests/config', 'config-test')


def test_default_config_without_file():
    configuration.validate_config()


@pytest.mark.usefixtures("load_config")
def test_config_for_tests_validation():
    configuration.validate_config()


@pytest.mark.usefixtures("load_config")
def test_weather_wrong_unit():
    wrong_unit = 'X'
    configuration.v.all_settings()['modes']['weather']['unit'] = wrong_unit

    with pytest.raises(ValidationError, match=wrong_unit):
        configuration.validate_config()


@pytest.mark.usefixtures("load_config")
@pytest.mark.parametrize("from_code,to_code,expected_error,error_matcher", [
    ('eur', 'usd', False, None),
    ('CHF', 'PLN', False, None),
    ('eurr', 'usd', True, 'eurr'),
    (None, 'usd', True, 'None'),
    ('EUR', None, True, 'None'),
])
def test_exchange_rate_wrong_currency_code(from_code, to_code, expected_error, error_matcher):
    configuration.v.all_settings()['modes']['exchange_rate']['types'].append({'from': from_code, 'to': to_code})

    if expected_error:
        with pytest.raises(ValidationError, match=error_matcher):
            configuration.validate_config()
    else:
        configuration.validate_config()


@pytest.mark.usefixtures("load_config")
def test_instagram_no_api_key():
    configuration.v.all_settings()['modes']['instagram']['api_key'] = None

    with pytest.raises(ValidationError, match='None'):
        configuration.validate_config()


@pytest.mark.usefixtures("load_config")
@pytest.mark.parametrize("default,increase_on_click,maximum,expected_error,error_matcher", [
    (0, 15, 15, False, None),
    (-1, 1, 5, True, '-1'),
    (0, 0, 15, True, '0'),
    (0, 1, 16, True, '16'),
])
def test_brightness_standard(default, increase_on_click, maximum, expected_error, error_matcher):
    settings = configuration.v.all_settings()
    settings['brightness']['standard']['default'] = default
    settings['brightness']['standard']['increase_on_click'] = increase_on_click
    settings['brightness']['standard']['max'] = maximum

    if expected_error:
        with pytest.raises(ValidationError, match=error_matcher):
            configuration.validate_config()
    else:
        configuration.validate_config()


@pytest.mark.usefixtures("load_config")
@pytest.mark.parametrize("time,value,expected_error,error_matcher", [
    ('00:00', 0, False, None),
    ('23:59', 15, False, None),
    ('6:00', 1, True, '6:00'),
    ('24:00', 1, True, '24:00'),
    ('12:30', -1, True, '-1'),
    ('12:30', 16, True, '16'),
    ('12:30', None, True, 'None'),
    (12.55, 1, True, '12.55'),
    (None, 7, True, 'None'),
])
def test_brightness_time_dependent_times(time, value, expected_error, error_matcher):
    settings = configuration.v.all_settings()
    settings['brightness']['mode'] = 'time_dependent'
    settings['brightness']['time_dependent']['times'].append({'from': time, 'value': value})

    if expected_error:
        with pytest.raises(ValidationError, match=error_matcher):
            configuration.validate_config()
    else:
        configuration.validate_config()
