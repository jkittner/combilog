from datetime import datetime
from struct import unpack
from typing import Any
from typing import Dict
from typing import List
from typing import Union

import serial


class ChannelNotFoundError(Exception):
    '''Raised when the logger channel is not found'''
    pass


class ChannelError(Exception):
    '''Raised when reading a channel that indicates an error'''
    pass


class CallNotSuccessfullError(Exception):
    '''Raised when a call was not sucessfull and the logger returned NAK'''
    pass


class Combilog():
    '''
    :port str: port the logger is connected to e.g. com3 or /dev/ttyACM0
    :logger_addr str|int: address of the logger as specified in the
        logger settings
    :baudrate int: baudrate as specified in the logger setup. Must be either
        2400, 4800, 9600 (default), 19200, 38400
    :bytesize int: bytesite as specified in the logger setup. Must be either
        5, 6, 7, 8 (default)
    :parity str: parity as specified in the logger settings. Must be either
        "N": None (default), "E": Even, "O": Odd
    :stopbits int: number of stopbits as specified in the logger settings.
        Must be either 1 or 2
    :timeout float: timeout as specified in the logger settings in seconds
    '''

    def __init__(
        self,
        logger_addr: Union[str, int],
        port: str,
        baudrate: int = 9600,
        bytesize: int = 8,
        parity: str = 'N',
        stopbits: int = 1,
        timeout: float = 1.0,
    ) -> None:
        BAUDRATE = (2400, 4800, 9600, 19200, 38400)
        BYTESIZE = (5, 6, 7, 8)
        PARITY = ('N', 'E', 'O')
        STOPBITS = (1, 2)

        # check input
        if baudrate not in BAUDRATE:
            raise ValueError(
                f'baudrate must be {", ".join(str(i) for i in BAUDRATE)}'
                f', not {baudrate}',
            )
        if bytesize not in BYTESIZE:
            raise ValueError(
                f'bytesize must be {", ".join(str(i) for i in BYTESIZE)}'
                f', not {bytesize}',
            )
        if parity not in PARITY:
            raise ValueError(
                f'parity must be {", ".join(str(i) for i in PARITY)}'
                f', not {parity}',
            )
        if stopbits not in STOPBITS:
            raise ValueError(
                f'stopbits must be {", ".join(str(i) for i in STOPBITS)}'
                f', not {stopbits}',
            )
        if not isinstance(timeout, float):
            raise TypeError(f'timeout must be float, not {type(timeout)}')

        self.logger_addr = str(logger_addr)
        # add leading 0 if only one digit
        if len(self.logger_addr) == 1:
            self.logger_addr = '0' + self.logger_addr

        # initialze serial object do not open
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.bytesize = bytesize
        self.ser.parity = parity
        self.ser.stopbits = stopbits
        self.ser.timeout = timeout

    def authenticate(self, passwd: str) -> bool:
        '''
        :passwd str: password as specified via the logger's webserver
        '''
        with self.ser as ser:
            telegram = f'${self.logger_addr}P{passwd}\r'.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        if resp == b'\x06':
            return True
        else:
            return False

    def device_id(self) -> Dict[str, str]:
        '''
        get the device identification containing:
        vendor name (e.g. Friedrichs), model name (e.g. COM1020)
        hw_revision (hardware ver), sw_revission (software/frimware ver)
        '''
        with self.ser as ser:
            telegram = f'${self.logger_addr}V\r'.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        info = resp.decode('latin-1')[1:]
        dev_id = {
            'vendor_name': info[0:10],
            'model_name': info[10:17],
            'hw_revision': info[18:23],
            'sw_revision': info[24:28],
        }
        return dev_id

    def device_info(self) -> Dict[str, Union[str, int]]:
        '''
        get the device information containing:
        location, serial number, number of channels
        '''
        with self.ser as ser:
            telegram = f'${self.logger_addr}S\r'.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        info = resp.decode('latin-1')[1:]
        dev_info = {
            'location': info[:20].strip(),
            'serial_number': int(info[20:26]),
            'nr_channels': int(info[26:].strip()),
        }
        return dev_info

    def status_info(self) -> Dict[str, str]:
        '''
        get the device status and see if there are any errors
        read about the codes in the manual pp 124-125
        '''
        with self.ser as ser:
            telegram = f'${self.logger_addr}Z\r'.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        info = resp.decode('latin-1')[1:]
        status_info = {
            'channel_status': info[:8],
            'module_status': info[9:],
        }
        return status_info

    def get_channel_info(self, channel_nr: str) -> Dict[str, str]:
        '''
        :channel_nr str: number of the channel to get information from
        must be from '01' to '20' (internal channels)
        or '80' to 'BB' (external channels)
        values are hexadecimal in only uppercase
        '''
        with self.ser as ser:
            telegram = f'${self.logger_addr}B{channel_nr}\r'.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
            success = (resp != b'\x15' and resp != b'')
        if success:
            info = resp.decode('latin-1')[1:]  # skip '=...'
            channel_info = {
                'channel_type': _channel_type_to_txt(int(info[0])),
                'channel_notation': info[1:20].strip(),
                'data_format': _data_format_to_txt(int(info[21])),
                'field_length': int(info[22]),
                'decimals': int(info[23]),
                'unit': info[24:29].strip(),
                'host_input': _host_input_possible(int(info[30])),
                'type_of_calculation': _channel_calc_to_txt(int(info[31])),
            }
            return channel_info
        else:
            raise ChannelNotFoundError(f'channel {channel_nr} was not found')

    def get_channel_list(self) -> List[str]:
        # internal channels
        INT_CHANNEL = [str(i) for i in list(range(1, 20))]
        # add leading 0 to channel numbers
        for i in range(0, 9):
            INT_CHANNEL[i] = f'0{i+1}'
        int_channel_list = []
        for j in INT_CHANNEL:
            try:
                info = self.get_channel_info(j)
                int_channel_list.append(info['channel_notation'])
            except ChannelNotFoundError:
                pass
        # TODO: get external channels
        # for some reason an empty external channel has len 31 not 32
        # as specified in the manual so this is broken
        """
        EXT_CHANNEL = [str(hex(i))[2:].upper() for i in list(range(128, 188))]
        ext_channel_list = []
        for i in EXT_CHANNEL:
            try:
                info = self.get_channel_info(i)
                ext_channel_list.append(info['channel_notation'])
            except:
                pass
        """
        channel_list = int_channel_list
        return channel_list

    def read_channel(self, channel_nr: str):
        with self.ser as ser:
            telegram = f'${self.logger_addr}R{channel_nr}\r'.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        channel = resp.decode('latin-1')[1:]
        if channel.startswith('E'):
            raise ChannelError(
                f'Cannot read channel {channel_nr}, '
                'the channel indicates an error',
            )
        return channel.strip()

    def write_channel(
        self,
        channel_nr: str,
        channel_value: Union[float, int, str],
    ) -> None:
        '''
        Write to a channel --> set the channel to a specific value
        a previous Authentication is required! (self.authenticate(passwd=...))
        '''
        with self.ser as ser:
            telegram = (
                f'${self.logger_addr}W{channel_nr}{channel_value}\r'
            ).encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        if resp != b'\x06':
            raise CallNotSuccessfullError(
                f'Unable write to channel {channel_nr}. '
                'Did you authenticate and does the channel exist?',
            )

    def reset_channel(self, channel_nr: str) -> None:
        '''
        reset a channel e.g. reset the min/max value.
        a previous Authentication is required! (self.authenticate(passwd=...))
        :channel_nr: must be from '01' to '20' (internal channels)
        or '80' to 'BB' (external channels)
        '''
        with self.ser as ser:
            telegram = f'${self.logger_addr}D{channel_nr}\r'.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
            if resp != b'\x06':
                raise CallNotSuccessfullError(
                    f'Unable to reset channel {channel_nr}. '
                    'Did you authenticate and does the channel exist?',
                )

    def pointer_to_start(self, pointer: Union[str, int]) -> None:
        '''sets a pointer to start'''
        if str(pointer) == '1':
            call = 'C'
        elif str(pointer) == '2':
            call = 'c'
        else:
            raise ValueError(f'pointer must be either 1 or 2, not {pointer}')
        with self.ser as ser:
            telegram = f'${self.logger_addr}{call}\r'.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        if resp != b'\x06':
            raise CallNotSuccessfullError(
                'Unable to set pointer 1. Did you authenticate?',
            )

    def read_event(
        self,
        pointer: Union[str, int],
    ) -> Dict[str, List[float]]:
        '''
        read the event at the position of the pointer
        returns a dictionary with the timestamp as key
        if there are no events an empty dict is returned
        '''
        if str(pointer) == '1':
            call = 'E'
        elif str(pointer) == '2':
            call = 'e'
        else:
            raise ValueError(f'pointer must be either 1 or 2, not {pointer}')

        with self.ser as ser:
            telegram = f'${self.logger_addr}{call}\r'.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        if len(resp) > 3:
            events = resp.decode('latin-1')[1:].split(';')
            # the first char is the address and therefore not needed
            date = datetime.strptime(events[0][1:], '%y%m%d%H%M%S')
            # remove carriage return at the end
            # and convert from IEE Std 754 Short Real Format
            event = {
                str(date): [_hexIEE_to_dec(i) for i in events[1:-1]],
            }
            return event
        else:
            return {}

    def repeat_read_event(
        self,
        pointer: Union[str, int],
    ) -> Dict[str, List[float]]:
        '''
        read an event from the logger's storage
        '''
        if str(pointer) == '1':
            call = 'F'
        elif str(pointer) == '2':
            call = 'f'
        else:
            raise ValueError(f'pointer must be either 1 or 2, not {pointer}')

        with self.ser as ser:
            telegram = f'${self.logger_addr}{call}\r'.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        if len(resp) > 3:
            events = resp.decode('latin-1')[1:].split(';')
            # the first char is the address and therefore not needed
            date = datetime.strptime(events[0][1:], '%y%m%d%H%M%S')
            # remove carriage return at the end
            # and convert from IEE Std 754 Short Real Format
            event = {
                str(date): [_hexIEE_to_dec(i) for i in events[1:-1]],
            }
            return event
        else:
            return {}

    def pointer_to_date(
        self,
        pointer: Union[str, int],
        date: Union[str, datetime],
    ) -> None:
        '''
        sets pointer 1 to a specific date
        :date: str with Format '%y%m%d%H%M%S' or a datetime.dateime object
        '''
        if str(pointer) == '1':
            call = 'C'
        elif str(pointer) == '2':
            call = 'c'
        else:
            raise ValueError(f'pointer must be either 1 or 2, not {pointer}')
        if isinstance(date, datetime):
            date = date.strftime('%y%m%d%H%M%S')
        if len(date) != 12:
            raise ValueError(
                f'date must have len 12, not {len(date)} '
                'and must have the format %y%m%d%H%M%S',
            )
        with self.ser as ser:
            telegram = f'${self.logger_addr}{call}{date}\r'.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        if resp != b'\x06':
            raise CallNotSuccessfullError(
                f'Unable to set pointer 1 to {date}. Did you authenticate? '
                'has "date" the format %y%m%d%H%M%S or is a datetime.datetime'
                ' object?',
            )

    def pointer_to_pos(
        self,
        pointer: Union[str, int],
        position: str,
    ) -> None:
        '''
        sets pointer 1 to a specific position
        '''
        if str(pointer) == '1':
            call = 'C'
        elif str(pointer) == '2':
            call = 'c'
        else:
            raise ValueError(f'pointer must be either 1 or 2, not {pointer}')
        with self.ser as ser:
            telegram_str = f'${self.logger_addr}{call}{position}\r'
            telegram = telegram_str.encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        if resp != b'\x06':
            raise CallNotSuccessfullError(
                f'Unable to set pointer 1 to position {position}. '
                'Did you authenticate?',
            )

    def set_datetime(
        self,
        date: Union[str, datetime] = datetime.now(),
    ) -> None:
        '''
        Set the logger's clock (default is computer time)
        a previous Authentication is required!
        '''
        if isinstance(date, datetime):
            date = date.strftime('%y%m%d%H%M%S')
        if len(date) != 12:
            raise ValueError(
                f'date must have len 12, not {len(date)} '
                'and must have the format %y%m%d%H%M%S',
            )
        with self.ser as ser:
            telegram = (f'${self.logger_addr}G{date}\r').encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        if resp != b'\x06':
            raise CallNotSuccessfullError(
                f'Unable to set the date to {date}. '
                'Did you authenticate?',
            )

    def read_datetime(self) -> datetime:
        '''read the time and return it as a datetime.datetime object'''
        with self.ser as ser:
            telegram = (f'${self.logger_addr}H\r').encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        resp_str = resp.decode('latin-1')[1:-1]
        logger_datetime = datetime.strptime(resp_str, '%y%m%d%H%M%S')
        return logger_datetime

    def get_rate(self) -> Dict[str, int]:
        '''get the measuring and averaging rate in seconds'''
        with self.ser as ser:
            telegram = (f'${self.logger_addr}X\r').encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        rates_str = resp.decode('latin-1')[1:]
        rates = {
            'measuring_rate': int(rates_str[0:2]),
            'averaging_interval': int(rates_str[2:7]),
        }
        return rates

    def set_rate(
        self,
        measuring_rate: int,
        averaging_interval: int,
    ) -> None:
        '''set the logger's measuring and averaging rate'''
        if measuring_rate > 100:
            raise ValueError('Cannot set measuring rate higher than 99')
        if averaging_interval > 43200:
            raise ValueError('max averaging interval rate is 43200 (12h)')
        # bring to correct length
        len_averaging_interval = len(str(averaging_interval))
        if len(str(measuring_rate)) < 2:
            measuring_rate_str = '0' + str(measuring_rate)
        else:
            measuring_rate_str = str(measuring_rate)

        if len_averaging_interval < 5:
            averaging_interval_str = ((5 - len_averaging_interval) * '0'
                                      + str(averaging_interval))
        else:
            averaging_interval_str = str(averaging_interval)

        rate = f'{measuring_rate_str}{averaging_interval_str}'
        with self.ser as ser:
            telegram = (f'${self.logger_addr}Y{rate}\r').encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        if resp != b'\x06':
            raise CallNotSuccessfullError(
                f'Unable to set the rate to {measuring_rate} '
                f'and {averaging_interval}. Did you authenticate?',
            )

    def delete_memory(self) -> None:
        '''deletes the logger storage cannot be undone!'''
        with self.ser as ser:
            telegram = (f'${self.logger_addr}C.ALL\r').encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        if resp != b'\x06':
            raise CallNotSuccessfullError(
                "Unable to delete the logger's storage. "
                'Did you authenticate?',
            )

    def get_nr_events(self) -> int:
        '''
        get the number of logs available with the currently set pointer
        '''
        with self.ser as ser:
            telegram = (f'${self.logger_addr}N\r').encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        logs = int(resp.decode('latin-1')[1:])
        return logs

    def transparent_mode(self, state: bool) -> None:
        '''switch the transparent mode on or off'''
        if state:
            call = 'T1'
        if not state:
            call = 'T2'

        with self.ser as ser:
            telegram = (f'${self.logger_addr}{call}\r').encode('latin-1')
            ser.write(telegram)
            resp = ser.read_until(b'\r')
        if resp != b'\x06':
            raise CallNotSuccessfullError(
                'Unable to change the state of the transparent modee.'
                'Did you authenticate?',
            )

    def read_logger(
        self,
        pointer: Union[str, int],
        verbose: bool = False,
        output_type: str = 'dict',
    ) -> Union[Dict[str, List[float]], List[Union[Any]]]:
        '''
        reads all bookings starting from the set pointer
        :pointer str|int: the pointer from where to read
        :verbose bool: print output to the stdout
        :output_type str: output as a "dict" which can be converted to a pd df
            output as "list" to be written to csv using the csv module
        depending on the number of logs this can take a while
        '''
        # get number of logs
        logs = self.get_nr_events()
        # read all events
        i = 0
        events = {}
        while i < logs:
            if verbose:
                print(f'reading event {i+1} of {logs}')
            event = self.read_event(pointer)
            events.update(event)
            i += 1
        if output_type == 'dict':
            return events
        elif output_type == 'list':
            list_events = []
            for j in events.keys():
                values = [k for k in events[j]]
                timestamp_values = [j] + values  # type: ignore
                list_events.append(timestamp_values)
            return list_events
        else:
            raise ValueError(
                f'output_type must be dict or list, not {output_type}',
            )


def _channel_type_to_txt(channel_type: int) -> str:
    CHANNEL_TYPES = {
        0: 'empty channel (EM)',
        1: 'analogue input channel (AR)',
        2: 'arithmeic channel (AR)',
        3: 'digital output channel (DO)',
        4: 'digital input channel (DI)',
        5: 'setpoint channel (VO)',
        6: 'alarm channel (AL)',
    }
    try:
        return CHANNEL_TYPES[channel_type]
    except KeyError:
        return 'unknown channel type'


def _channel_calc_to_txt(calc_type: int) -> str:
    CALC_TYPES = {
        0: 'normal calculation of average value',
        1: 'calculation of average value with wind direction',
        2: 'calculation of the sum over the averaging interval',
        3: 'continuous sum',
        4: 'vectorial average for wind velocity',
        5: 'vectorial average for wind direction',
    }
    try:
        return CALC_TYPES[calc_type]
    except KeyError:
        return 'unknown calculation type'


def _data_format_to_txt(data_format: int) -> str:
    DATA_FORMATS = {
        0: 'no format',
        1: 'bool',
        2: 'integer',
        3: 'real',
        4: 'set 8',
    }
    try:
        return DATA_FORMATS[data_format]
    except KeyError:
        return 'unknown data format'


def _host_input_possible(host_input: int) -> Union[bool, str]:
    if host_input == 0:
        return True
    elif host_input == 1:
        return False
    else:
        return 'unknown'


def _hexIEE_to_dec(hexval: str, digits: int = 2) -> float:
    '''decode the data read from the logger's storage drive'''
    dec = round(unpack('!f', bytes.fromhex(hexval))[0], digits)
    return dec
