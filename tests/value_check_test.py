import pytest

from combilog import Combilog


def test_raises_value_error_invalid_baudrate():
    invalid_baudrate = 12345
    with pytest.raises(ValueError) as execinfo:
        Combilog(
            logger_addr=1,
            port='com6',
            baudrate=invalid_baudrate,
        )
    # check error msg contains allowed values and given value
    assert '2400, 4800, 9600, 19200, 38400' in str(execinfo.value)
    assert str(invalid_baudrate) in str(execinfo.value)


def test_raises_value_error_invalid_bytesize():
    invalid_bytesize = 12345
    with pytest.raises(ValueError) as execinfo:
        Combilog(
            logger_addr=1,
            port='com6',
            bytesize=invalid_bytesize,
        )
    # check error msg contains allowed values and given value
    assert '5, 6, 7, 8' in str(execinfo.value)
    assert str(invalid_bytesize) in str(execinfo.value)


def test_raises_value_error_invalid_parity():
    invalid_parity = '12345'
    with pytest.raises(ValueError) as execinfo:
        Combilog(
            logger_addr=1,
            port='com6',
            parity=invalid_parity,
        )
    # check error msg contains allowed values and given value
    assert 'N, E, O' in str(execinfo.value)
    assert str(invalid_parity) in str(execinfo.value)


def test_raises_value_error_invalid_stopbits():
    invalid_stopbits = 12345
    with pytest.raises(ValueError) as execinfo:
        Combilog(
            logger_addr=1,
            port='com6',
            stopbits=invalid_stopbits,
        )
    # check error msg contains allowed values and given value
    assert '1, 2' in str(execinfo.value)
    assert str(invalid_stopbits) in str(execinfo.value)


def test_raises_type_error_invalid_timeout():
    invalid_timeout = '10 seconds'
    with pytest.raises(TypeError) as execinfo:
        Combilog(
            logger_addr=1,
            port='com6',
            timeout=invalid_timeout,  # type: ignore
        )
    # check error msg contains allowed values and given value
    assert 'float' in str(execinfo.value)
    assert "<class 'str'>" in str(execinfo.value)
