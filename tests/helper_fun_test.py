import pytest

from combilog import _channel_calc_to_txt
from combilog import _channel_type_to_txt
from combilog import _data_format_to_txt
from combilog import _hexIEE_to_dec
from combilog import _host_input_possible


@pytest.mark.parametrize(
    ('channel_type', 'exp_txt'),
    (
        (0, 'empty channel (EM)'),
        (1, 'analogue input channel (AR)'),
        (2, 'arithmeic channel (AR)'),
        (3, 'digital output channel (DO)'),
        (4, 'digital input channel (DI)'),
        (5, 'setpoint channel (VO)'),
        (6, 'alarm channel (AL)'),
        (13, 'unknown channel type'),
    ),
)
def test_get_channel_type(channel_type, exp_txt):
    channel_type = _channel_type_to_txt(channel_type=channel_type)
    assert channel_type == exp_txt


@pytest.mark.parametrize(
    ('calc_type', 'exp_txt'),
    (
        (0, 'normal calculation of average value'),
        (1, 'calculation of average value with wind direction'),
        (2, 'calculation of the sum over the averaging interval'),
        (3, 'continuous sum'),
        (4, 'vectorial average for wind velocity'),
        (5, 'vectorial average for wind direction'),
        (13, 'unknown calculation type'),
    ),
)
def test_get_calc_test(calc_type, exp_txt):
    calc_type = _channel_calc_to_txt(calc_type=calc_type)
    assert calc_type == exp_txt


@pytest.mark.parametrize(
    ('inp', 'exp'),
    (
        (0, True),
        (1, False),
        (13, 'unknown'),
    ),
)
def test_host_input(inp, exp):
    assert _host_input_possible(inp) == exp


@pytest.mark.parametrize(
    ('data_format', 'exp_txt'),
    (
        (0, 'no format'),
        (1, 'bool'),
        (2, 'integer'),
        (3, 'real'),
        (4, 'set 8'),
        (13, 'unknown data format'),
    ),
)
def test_get_data_format(data_format, exp_txt):
    data_format = _data_format_to_txt(data_format)
    assert data_format == exp_txt


@pytest.mark.parametrize(
    ('val', 'exp'),
    (
        ('00000000', 0),
        ('42493CD3', 50.31),
    ),
)
def test_hexIEE_to_dec(val, exp):
    resp_0 = _hexIEE_to_dec(val)
    assert resp_0 == exp
