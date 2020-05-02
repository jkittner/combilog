# classes for combilog_read_data.py
# Github: theendlessriver13/combilog1022
# Jonas Kittner 2020
from datetime import datetime
from struct import unpack

import pandas as pd
import serial


class telegram:

    @classmethod
    def createTG(cls, ser: serial.Serial, address: str, *argv: str) -> bytes:
        '''build a telegram an make a call'''
        tgStr = '$' + address
        for arg in argv:
            tgStr += arg
        tgStr += '\r'
        tgByte = tgStr.encode('utf-8')
        ser.write(tgByte)
        re = ser.read_until(b'\r')
        return re

    @classmethod
    def checkRe(cls, answer: bytes) -> None:
        '''Check answer of calls that return only NAK or ACK'''
        if (answer == b'\x15'):
            raise Exception('NAK - call not successful')
        elif (answer == b'\x06'):
            print('ACK - call successful')
        else:
            raise Exception('unknown byte returned')

    @classmethod
    def hexIEE_dec(cls, hexval: str) -> float:
        '''decode the data read from the logger's storage drive'''
        dec = round(unpack('!f', bytes.fromhex(hexval))[0], 2)
        return dec


class combilog:

    def __init__(self, logger_params: dict) -> None:
        self.address = logger_params['address']
        self.passwd = logger_params['passwd']
        self.ser = logger_params['ser']
        self.cnames = logger_params['cnames']

    def auth(self) -> None:
        '''autheticate with password to set pointers or delete storage'''
        tgStr = '$' + self.address + 'P' + self.passwd + '\r'
        tgByte = tgStr.encode('utf-8')
        self.ser.write(tgByte)
        passwdRe = self.ser.read_until(b'\r')
        telegram.checkRe(passwdRe)

    def pointer1_tostart(self) -> None:
        '''sets pointer 1 to start'''
        tg = telegram.createTG(self.ser, self.address, 'C')
        telegram.checkRe(tg)

    def pointer1_to_date(self, date: datetime) -> None:
        '''sets pointer 1 to a specific date and time'''
        date = datetime.strftime(date, '%y%m%d%H%M%S')
        tg = telegram.createTG(self.ser, self.address, 'C', date)
        telegram.checkRe(tg)

    def pointer1_to_pos(self, pos: str) -> None:
        '''sets pointer 1 to a specific position'''
        tg = telegram.createTG(self.ser, self.address, 'C', pos)
        telegram.checkRe(tg)

    def read_bookings_pt1(self, arg: str = 'E') -> pd.DataFrame:
        '''
        reads all bookings for the currently set pointer 1
        returns a pandas dataframe with all data
        '''
        i = 0
        df = pd.DataFrame(columns=self.cnames)
        logs = int(telegram.createTG(self.ser, self.address, 'N')[1:])
        while i < logs:
            row = telegram.createTG(self.ser, self.address, arg)[1:]
            row = row.decode('ascii')
            row = row.split(';')
            date = row[0][1:]
            date = datetime.strptime(date, '%y%m%d%H%M%S')
            datalist = row[1:-1]
            name = row[0][0]

            tmpList = []
            for item in datalist:
                element = telegram.hexIEE_dec(item)
                tmpList.append(element)

            tmpList.insert(0, str(date))
            tmpList.insert(0, int(name))
            dftmp = pd.DataFrame([tmpList], columns=self.cnames)
            df = df.append(dftmp)
            i += 1
            print(f'reading log: {i} of {logs}')
        return df

    def repeat_reading_pt1(self) -> pd.DataFrame:
        df = combilog.read_bookings_pt1(self, 'F')
        return df

    def pointer2_tostart(self) -> None:
        '''sets pointer 2 to start'''
        tg = telegram.createTG(self.ser, self.address, 'c')
        telegram.checkRe(tg)

    def pointer2_to_date(self, date: datetime) -> None:
        '''sets pointer 2 to a specific date and time'''
        date = datetime.strftime(date, '%y%m%d%H%M%S')
        tg = telegram.createTG(self.ser, self.address, 'c', date)
        telegram.checkRe(tg)

    def pointer2_to_pos(self, pos: str) -> None:
        '''sets pointer 1 to a specific position'''
        tg = telegram.createTG(self.ser, self.address, 'c', pos)
        telegram.checkRe(tg)

    def read_bookings_pt2(self) -> pd.DataFrame:
        '''
        reads all bookings for the currently set pointer 2
        returns a pandas dataframe with all data
        '''
        df = combilog.read_bookings_pt1(self, 'e')
        return df

    def repeat_reading_pt2(self) -> pd.DataFrame:
        df = combilog.read_bookings_pt1(self, 'f')
        return df

    def nr_logs(self) -> int:
        '''checks how many logs are available with the currently set pointer'''
        logs = int(telegram.createTG(self.ser, self.address, 'N')[1:])
        return logs

    def del_stor(self) -> None:
        '''deletes the logger storage cannot be undone!'''
        tg = telegram.createTG(self.ser, self.address, 'C.ALL')
        telegram.checkRe(tg)

    def read_channel(self, channelNr: str) -> float:
        '''
        reads a specific channel on the logger
        channelNr must be type str and must have
        the format '01'-'20' or '80'-'BB'
        '''
        tg = telegram.createTG(self.ser, self.address, 'R', channelNr)
        tg = float(tg.decode('ascii')[1:])
        return tg

    def read_datetime(self) -> datetime:
        '''reads the current logger time'''
        tg = telegram.createTG(self.ser, self.address, 'H')
        tg = tg.decode('ascii')[1:-1]
        tg = datetime.strptime(tg, '%y%m%d%H%M%S')
        return tg

    def set_datetime(self, newTime: datetime = datetime.now()) -> None:
        '''
        newTime = time to set the logger clock to. Default is the system time
        else newTime must be a datetime object
        '''
        newTime = datetime.strftime(newTime, '%y%m%d%H%M%S')
        tg = telegram.createTG(self.ser, self.address, 'G', newTime)
        telegram.checkRe(tg)

    def dev_id(self) -> dict:
        '''reads the device identification'''
        tg = telegram.createTG(self.ser, self.address, 'V')
        tg = tg.decode('ascii')[1:]
        device_id = {
            'vendor_name': tg[0:9],
            'model_name':  tg[10:17],
            'hw_revision': tg[18:23],
            'sw_revision': tg[24:28],
        }
        return device_id

    def dev_info(self) -> dict:
        '''reads the device information'''
        tg = telegram.createTG(self.ser, self.address, 'S')
        tg = tg.decode('ascii')[1:]
        # remove trailing whitespace in location
        device_info = {
            'location':      tg[0:19].strip(),
            'serial_number': tg[20:26],
            'nr_channels':   tg[26:28],
        }
        return device_info

    def dev_status(self) -> dict:
        '''returns the channel and module status'''
        # TODO: parse the bits to define the error
        tg = telegram.createTG(self.ser, self.address, 'Z')
        tg = tg.decode('ascii')[1:]
        device_status = {
            'channel_status': tg[0:8],
            'module_status': tg[8:12],
        }
        return device_status

    def channel_info(self, channelNr: str) -> dict:
        '''returns all channel information'''
        # FIXME: ° = 0xb0 raises:
        # UnicodeDecodeError: 'ascii' codec can't decode byte 0xb0
        # in position 25: ordinal not in range(128)
        # TODO: Parse e.g. dataformat what means '3'
        tg = telegram.createTG(self.ser, self.address, 'B', channelNr)
        tg = tg.decode('ascii')[1:]

        # channel type
        channel_type = tg[0]
        if channel_type == '0':
            channel_type = 'empty channel (EM)'
        elif channel_type == '1':
            channel_type = 'analogue input channel (AR)'
        elif channel_type == '2':
            channel_type = 'arithmeic channel (AR)'
        elif channel_type == '3':
            channel_type = 'digital output channel (DO)'
        elif channel_type == '4':
            channel_type = 'digital input channel (DI)'
        elif channel_type == '5':
            channel_type = 'setpoint channel (VO)',
        elif channel_type == '6':
            channel_type = 'alarm channel (AL)'
        else:
            channel_type = 'unknown channel type'

        # type of calcualtion
        type_of_calculation = tg[31]
        if type_of_calculation == '0':
            type_of_calculation = 'normal calculation of average value'
        elif type_of_calculation == '1':
            type_of_calculation = 'calculation of average value with wind direction'  # noqa: E501
        elif type_of_calculation == '2':
            type_of_calculation = 'calculation of the sum over the averaging interval'  # noqa: 501
        elif type_of_calculation == '3':
            type_of_calculation = 'continuous sum'
        elif type_of_calculation == '4':
            type_of_calculation = 'vectorial average for wind velocity'
        elif type_of_calculation == '5':
            type_of_calculation = 'vectorial average for wind direction',
        else:
            type_of_calculation = 'unknown type of calculation'

        channel_information = {
            'channel_type': channel_type,
            'channel_notation': tg[1:20].strip(),
            'data_format': tg[21],
            'field_length': tg[22],
            'decimals': tg[23],
            'unit': tg[24:29].strip(),
            'channel_configuration': tg[30],
            'type_of_calculation': type_of_calculation,
        }
        return channel_information

    def get_rate(self) -> dict:
        tg = telegram.createTG(self.ser, self.address, 'X')
        tg = tg.decode('ascii')[1:]
        rates = {
            'measuring_rate': tg[0:2],
            'averaging_interval': tg[2:7],
        }
        return rates

    def set_rate(self, rate: str) -> None:
        '''
        rate must be a str with len = 7
        first two chars are measuring rate in s last 5 are averaging rate in s
        '''
        tg = telegram.createTG(self.ser, self.address, 'Y', rate)
        telegram.checkRe(tg)

    def other_call(self, *argv: str) -> str:
        '''
        method to use for calls that are not defined in this class
        the data is returned as string and needs further processing
        '''
        argStr = ''
        for arg in argv:
            argStr += arg
        tg = telegram.createTG(self.ser, self.address, argStr)
        tg = tg.decode('ascii')
        return tg
