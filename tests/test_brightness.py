import pytest

from rpidisplay.brightness import Standard
from rpidisplay.brightness import TimeDependent
from tests.mocks import fake_datetime_provider
from tests.mocks import fake_device


@pytest.mark.usefixtures("load_config")
@pytest.mark.parametrize("default,increase_on_click,maximum,clicks,expected_level", [
    (0, 3, 15, 3, 9),
    (0, 6, 15, 3, 0),
    (0, 1, 5, 3, 3),
    (0, 4, 10, 4, 4),
    (0, 4, 12, 3, 12),
])
def test_standard(default, increase_on_click, maximum, clicks, expected_level):
    standard = Standard(fake_device)
    standard._default = default
    standard._increase_on_click = increase_on_click
    standard._max = maximum

    for _ in range(clicks):
        standard.on_click()

    assert standard._level == expected_level


@pytest.mark.usefixtures("load_config")
@pytest.mark.parametrize("time,expected_level", [
    ('00:00', 7),
    ('01:48', 7),
    ('01:49', 1),
    ('02:42', 2),
    ('02:43', 3),
    ('05:59', 3),
    ('06:00', 4),
    ('12:00', 5),
    ('21:00', 6),
    ('23:59', 7),
])
def test_time_dependent(time, expected_level):
    time_dependent = TimeDependent(fake_device)
    datetime_provider = fake_datetime_provider
    datetime_provider.current_time = time
    time_dependent._datetime_provider = datetime_provider

    time_dependent._watch_times()

    assert time_dependent._level == expected_level
