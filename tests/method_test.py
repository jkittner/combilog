import re
from datetime import datetime

import pytest

from combilog import CallNotSuccessfullError
from combilog import ChannelError
from combilog import ChannelNotFoundError


def test_authenticate_wrong_password(my_logger):
    auth = my_logger.authenticate(passwd='wrong_password')
    assert auth is False


def test_authenticate_successfull(my_logger):
    auth = my_logger.authenticate(passwd='12345678')
    assert auth is True


def test_get_channel_info_not_found(my_logger):
    invalid_channel = 'not_existing_channel'
    with pytest.raises(ChannelNotFoundError) as execinfo:
        my_logger.get_channel_info(channel_nr=invalid_channel)
    assert invalid_channel in str(execinfo.value)


def test_get_channel_info(my_logger):
    valid_channel = '01'
    resp = my_logger.get_channel_info(channel_nr=valid_channel)
    EXP_KEYS = [
        'channel_type', 'channel_notation', 'data_format',
        'field_length', 'decimals', 'unit', 'host_input',
        'type_of_calculation',
    ]
    for i in resp.keys():
        assert i in EXP_KEYS

    assert resp['channel_type'] == 'analogue input channel (AR)'
    assert resp['decimals'] == 1
    assert resp['field_length'] == 4


def test_get_channel_list(my_logger):
    channel_list = my_logger.get_channel_list()
    EXP_INT_CHANNELS = [
        'LufttempMittel', 'LufttempMin', 'LufttempMax', 'LuftfeuchteMittel',
        'LuftfeuchteMin', 'LuftfeuchteMax', 'TaupunktMittel', 'TaupunktMin',
        'TaupunktMax', 'OberflTempMin', 'OberflTempMax', 'SonneStatus',
        'SonneDauer', 'DirektStrahlung', 'DirektStrahlMin', 'DirektStrahlMax',
        'Niederschlag', '°²³%$§"!',
    ]
    for i in channel_list:
        assert i in EXP_INT_CHANNELS

    # TODO: Add external channels


def test_get_device_id(my_logger):
    dev_id = my_logger.device_id()
    EXP_KEYS = ['vendor_name', 'model_name', 'hw_revision', 'sw_revision']
    for i in dev_id.keys():
        assert i in EXP_KEYS

    assert dev_id['vendor_name'] == 'Friedrichs'
    assert dev_id['sw_revision'] == '2.26'


def test_get_device_info(my_logger):
    dev_info = my_logger.device_info()
    EXP_KEYS = ['location', 'serial_number', 'nr_channels']
    for i in dev_info.keys():
        assert i in EXP_KEYS

    assert dev_info['location'] == 'DachSoni'
    assert dev_info['serial_number'] == 100005
    assert dev_info['nr_channels'] == 18


def test_get_status_info(my_logger):
    status_info = my_logger.status_info()
    assert len(status_info['channel_status']) == 8
    assert len(status_info['module_status']) == 4


def test_read_channel_success(my_logger):
    channel = my_logger.read_channel('05')
    assert len(channel) == 3
    assert '.' in channel


def test_read_channel_error(my_logger):
    with pytest.raises(ChannelError) as execinfo:
        my_logger.read_channel('01')
    assert '01' in str(execinfo.value)
    assert 'Cannot read' in str(execinfo.value)


def test_write_channel_success(my_logger):
    my_logger.authenticate('12345678')
    # must not raise an error when successfull
    my_logger.write_channel('08', '10.0')


def test_write_channel_error(my_logger):
    my_logger.authenticate('12345678')
    # must raise an error becuase channel does not exist
    with pytest.raises(CallNotSuccessfullError) as execinfo:
        my_logger.write_channel('20', '10.0')
    assert 'channel 20' in str(execinfo.value)


def test_reset_channel_success(my_logger):
    my_logger.authenticate('12345678')
    # raises an error when not successfull
    my_logger.reset_channel('05')


def test_reset_channel_error(my_logger):
    my_logger.authenticate('12345678')
    # raises an error when not successfull
    invalid_channel = '20'
    with pytest.raises(CallNotSuccessfullError) as execinfo:
        my_logger.reset_channel(invalid_channel)
    assert invalid_channel in str(execinfo.value)


@pytest.mark.parametrize('pointer', ('1', 2))
def test_set_pointer_to_start(pointer, my_logger):
    # if not successfull it raises an error
    assert my_logger.pointer_to_start(pointer) is None


def test_set_pointer_to_start_invalid_pointer(my_logger):
    invalid_pointer = '5'
    with pytest.raises(ValueError) as execinfo:
        my_logger.pointer_to_start(invalid_pointer)
    assert invalid_pointer in str(execinfo.value)


@pytest.mark.parametrize('pointer', ('1', 2))
def test_read_event(pointer, my_logger):
    my_logger.authenticate('12345678')
    my_logger.pointer_to_start(pointer)
    events = my_logger.read_event(pointer)
    # get dict key --> must only be one
    timestamp = [i for i in events.keys()]
    assert len(timestamp) == 1
    assert len(events[timestamp[0]]) == 22


def test_read_event_invalid_pointer(my_logger):
    my_logger.authenticate('12345678')
    invalid_pointer = '5'
    with pytest.raises(ValueError) as execinfo:
        my_logger.read_event(invalid_pointer)
    assert invalid_pointer in str(execinfo.value)


@pytest.mark.parametrize('pointer', ('1', 2))
def test_repeat_read_event(pointer, my_logger):
    my_logger.authenticate('12345678')
    my_logger.pointer_to_start(pointer)
    event = my_logger.repeat_read_event(pointer)
    # get dict key --> must only be one
    timestamp = [i for i in event.keys()]
    assert len(timestamp) == 1
    assert len(event[timestamp[0]]) == 22


def test_repeat_read_event_invalid_pointer(my_logger):
    my_logger.authenticate('12345678')
    invalid_pointer = '5'
    with pytest.raises(ValueError) as execinfo:
        my_logger.repeat_read_event(invalid_pointer)
    assert invalid_pointer in str(execinfo.value)


@pytest.mark.parametrize('pointer', ('1', 2))
def test_set_pointer_to_date_str(pointer, my_logger):
    my_logger.authenticate('12345678')
    # if not successfull it raises an error
    assert my_logger.pointer_to_date(pointer, '200904172000') is None


def test_set_pointer_to_date_invalid_pointer(my_logger):
    my_logger.authenticate('12345678')
    invalid_pointer = '5'
    with pytest.raises(ValueError) as execinfo:
        my_logger.pointer_to_date(invalid_pointer, '200904172000')
    assert invalid_pointer in str(execinfo.value)


@pytest.mark.parametrize('pointer', ('1', 2))
def test_set_pointer_to_date_datetime(pointer, my_logger):
    my_logger.authenticate('12345678')
    date = datetime(
        year=2020,
        month=9,
        day=4,
        hour=17,
        minute=20,
        second=0,
    )
    # if not successfull it raises an error
    assert my_logger.pointer_to_date(pointer, date) is None


@pytest.mark.parametrize('pointer', ('1', 2))
def test_set_pointer_to_date_invalid_str(pointer, my_logger):
    my_logger.authenticate('12345678')
    # if not successfull it raises an error
    invalid_date_str = '20090417'
    date_len = len(invalid_date_str)
    with pytest.raises(ValueError) as execinfo:
        my_logger.pointer_to_date(pointer, invalid_date_str)
    assert str(date_len) in str(execinfo.value)
    assert '%y%m%d%H%M%S' in str(execinfo.value)


@pytest.mark.parametrize('pointer', ('1', 2))
def test_set_pointer_to_position(pointer, my_logger):
    my_logger.authenticate('12345678')
    # if not successfull it raises an error
    position = '123'
    my_logger.pointer_to_pos(pointer, position)


def test_set_pointer_to_position_invalid_pointer(my_logger):
    my_logger.authenticate('12345678')
    invalid_pointer = '5'
    position = '123'
    with pytest.raises(ValueError) as execinfo:
        my_logger.pointer_to_pos(invalid_pointer, position)
    assert invalid_pointer in str(execinfo.value)


@pytest.mark.parametrize('date', ('200904172000', datetime.now()))
def test_set_datetime(date, my_logger):
    my_logger.authenticate('12345678')
    # if not successfull it raises an error
    my_logger.set_datetime(date=date)


def test_set_datetime_invalid_date(my_logger):
    my_logger.authenticate('12345678')
    # if not successfull it raises an error
    invalid_date = '2020-09-04 19:47:00'
    invalid_date_len = len(invalid_date)
    with pytest.raises(ValueError) as execinfo:
        my_logger.set_datetime(date=invalid_date)
    assert str(invalid_date_len) in str(execinfo.value)


def test_read_datetime(my_logger):
    my_logger.authenticate('12345678')
    time = my_logger.read_datetime()
    assert isinstance(time, datetime)


def test_get_rates(my_logger):
    rates = my_logger.get_rate()
    EXP_KEYS = ['measuring_rate', 'averaging_interval']
    keys = list(rates.keys())
    for i in keys:
        assert i in EXP_KEYS
    assert isinstance(rates['measuring_rate'], int)


@pytest.mark.parametrize(
    ('measuring_rate', 'averaging_interval'),
    (
        pytest.param(5, 10, id='leading 0'),
        pytest.param(10, 10000, id='no leading 0'),
    ),
)
def test_set_rate(my_logger, measuring_rate, averaging_interval):
    my_logger.authenticate('12345678')
    # get rate
    rates = my_logger.get_rate()
    measuring_rate_pre = rates['measuring_rate']
    averaging_interval_pre = rates['averaging_interval']
    my_logger.set_rate(measuring_rate, averaging_interval)
    # get new rates
    new_rates = my_logger.get_rate()
    assert new_rates['measuring_rate'] == measuring_rate
    assert new_rates['averaging_interval'] == averaging_interval
    # reset to old value
    my_logger.set_rate(measuring_rate_pre, averaging_interval_pre)


def test_set_rate_invalid_measuring_rate(my_logger):
    my_logger.authenticate('12345678')
    with pytest.raises(ValueError) as execinfo:
        my_logger.set_rate(measuring_rate=123456789, averaging_interval=1)
    assert 'higher than 99' in str(execinfo.value)


def test_set_rate_invalid_averaging_interval(my_logger):
    my_logger.authenticate('12345678')
    with pytest.raises(ValueError) as execinfo:
        my_logger.set_rate(measuring_rate=1, averaging_interval=123456789)
    assert 'rate is 43200' in str(execinfo.value)


def test_read_number_of_logs(my_logger):
    my_logger.authenticate('12345678')
    my_logger.pointer_to_start(pointer='1')
    logs = my_logger.get_nr_events()
    assert logs >= 0
    assert isinstance(logs, int)


def test_read_logger_not_verbose_dict(my_logger):
    # test will fail if no logs or only 1 are present
    my_logger.authenticate('12345678')
    my_logger.pointer_to_start(pointer=1)
    logs = my_logger.read_logger(pointer=1)
    # must have stored multiple logs
    keys = list(logs.keys())
    assert len(keys) > 1
    # key must be convertable to a datetime object
    date = datetime.strptime(keys[0], '%Y-%m-%d %H:%M:%S')
    assert isinstance(date, datetime)
    pattern = re.compile(
        r'20[2-9][0-9]-(0[1-9]|1[0-2])-'
        r'(0[1-9]|1[0-9]|2[0-9]|3[0-1]) (0[0-9]|1[0-9]|2[0-3]):'
        r'[0-5][0-9]:[0-5][0-9]',
    )
    assert re.match(pattern, keys[0])


def test_read_logger_verbose_dict(capsys, my_logger):
    # test will fail if no logs or only 1 are present
    my_logger.authenticate('12345678')
    my_logger.pointer_to_start(pointer=1)
    # get number of logs
    nr_logs = my_logger.get_nr_events()
    logs = my_logger.read_logger(pointer=1, verbose=True)
    # must have stored multiple logs
    keys = list(logs.keys())
    assert len(keys) > 1
    # key must be convertable to a datetime object
    date = datetime.strptime(keys[0], '%Y-%m-%d %H:%M:%S')
    assert isinstance(date, datetime)
    pattern = re.compile(
        r'20[2-9][0-9]-(0[1-9]|1[0-2])-'
        r'(0[1-9]|1[0-9]|2[0-9]|3[0-1]) (0[0-9]|1[0-9]|2[0-3]):'
        r'[0-5][0-9]:[0-5][0-9]',
    )
    assert re.match(pattern, keys[0])
    captured = capsys.readouterr()
    pattern_std_out = re.compile(r'reading\sevent\s\d+\sof\s\d+\n')
    matches = re.findall(pattern_std_out, captured.out)
    # every read invoked a print statement fails if another log was written
    assert len(matches) == nr_logs


def test_read_logger_verbose_list(my_logger, capsys):
    # test will fail if no logs or only 1 are present
    my_logger.authenticate('12345678')
    my_logger.pointer_to_start(pointer=1)
    # get number of logs
    nr_logs = my_logger.get_nr_events()
    logs = my_logger.read_logger(pointer=1, verbose=True, output_type='list')
    # got all logs
    assert isinstance(logs, list)
    assert isinstance(logs[0], list)
    assert isinstance(logs[0][0], str)
    assert isinstance(logs[0][1], float)
    assert len([i for i in logs]) == nr_logs
    captured = capsys.readouterr()
    pattern_std_out = re.compile(r'reading\sevent\s\d+\sof\s\d+\n')
    matches = re.findall(pattern_std_out, captured.out)
    # every read log invoked a print statement
    assert len(matches) == nr_logs


def test_read_logger_wrong_output_type(my_logger):
    my_logger.authenticate('12345678')
    my_logger.pointer_to_start(pointer=1)
    with pytest.raises(ValueError) as execinfo:
        my_logger.read_logger(pointer=1, output_type='invalid')
    assert 'invalid' in str(execinfo.value)
    assert 'dict' in str(execinfo.value)
    assert 'list' in str(execinfo.value)


def test_delete_memeory(my_logger):
    my_logger.authenticate('12345678')
    my_logger.pointer_to_start(pointer='1')
    logs_pre = my_logger.get_nr_events()
    assert logs_pre > 0
    my_logger.delete_memory()
    logs_del = my_logger.get_nr_events()
    assert logs_del == 0


@pytest.mark.skip(reason='there is no master network available for testing')
@pytest.mark.parametrize('state', (True, False))
def test_set_transparent_mode(my_logger, state):
    my_logger.authenticate('12345678')
    # raises an error if not successfull
    my_logger.transparent_mode(state)
