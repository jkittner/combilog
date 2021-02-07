import pytest

from combilog import Combilog


@pytest.fixture
def my_logger():
    return Combilog(logger_addr=1, port='com6')
