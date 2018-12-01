import pytest

from rpidisplay import configuration


@pytest.fixture
def load_config():
    configuration.setup_config('./tests/config', 'config-test')
