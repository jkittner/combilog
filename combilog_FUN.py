# classes for combilog_read_data.py
# Github: theendlessriver13/combilog1022
# (C) Jonas Kittner 2019

from   datetime import datetime
from   struct   import unpack
import pandas   as pd

class telegram:

    @classmethod
    def createTG(cls, ser, address, *argv):
        '''
        build telegram
        '''
        tgStr = '$' + address
        for arg in argv:
            tgStr += arg
        tgStr += '\r'
        tgByte = tgStr.encode('utf-8')
        ser.write(tgByte)
        re = ser.read_until(b'\r')
        return re

    @classmethod
    def checkRe(cls, answer):
        '''
        Check answer of calls that return only NAK or ACK
        '''
        if   (answer == b'\x15'):
            raise Exception('NAK - Call not succesessfull')
        elif (answer == b'\x06'):
            print('ACK - Call succesessfull')
        else:
            raise Exception('unknown Byte returned')

    @classmethod
    def hexIEE_dec(cls, hexval):
        '''
        decode the data read from the logger's storage drive
        '''
        return round(unpack('!f', bytes.fromhex(hexval))[0], 2)


class combilog:

    def __init__(self, logger_params):
        self.address = logger_params['address']
        self.passwd  = logger_params['passwd']
        self.ser     = logger_params['ser']
        self.cnames  = logger_params['cnames']
    
    def auth(self):
        '''
        autheticate with password
        '''
        tgStr    = '$' + self.address + 'P' + self.passwd + '\r'
        tgByte   = tgStr.encode('utf-8')
        self.ser.write(tgByte)
        passwdRe = self.ser.read_until(b'\r')
        telegram.checkRe(passwdRe)

    def pointer1_tostart(self):
        '''
        sets pointer1 to start
        '''
        tg = telegram.createTG(self.ser, self.address, 'C')
        telegram.checkRe(tg)
    
    def pointer1_to_date(self, date):
        '''
        sets pointer 1 to a specific date and time
        date must be str with format "%y%m%d%H%M%S"
        '''
        date = datetime.strftime(date, '%y%m%d%H%M%S')
        tg   = telegram.createTG(self.ser, self.address, 'C', date)
        telegram.checkRe(tg)

    def nr_logs(self):
        '''
        checks how many logs are available with the currently set pointer
        '''
        logs = int(telegram.createTG(self.ser, self.address, 'N')[1:])
        return logs

    def read_bookings_pt1(self):
        '''
        reads all bookings for the currently set pointer
        returns a pandas dataframe with all data
        '''
        i    = 0
        df   = pd.DataFrame(columns = self.cnames)
        logs = int(telegram.createTG(self.ser, self.address, 'N')[1:])
        while i < logs:
            row      = telegram.createTG(self.ser, self.address, 'E')[1:]
            row      = row.decode('ascii')
            row      = row.split(';')
            date     = row[0][1:]
            date     = datetime.strptime(date, '%y%m%d%H%M%S')
            datalist = row[1:-1]
            name     = row[0][0]

            tmpList = []
            for item in datalist:
                element = telegram.hexIEE_dec(item)
                tmpList.append(element)
            
            tmpList.insert(0, str(date))
            tmpList.insert(0, int(name))
            dftmp = pd.DataFrame([tmpList], columns = self.cnames)
            df    = df.append(dftmp)          
            i     += 1
            print('reading log: ', i, ' of ', logs)
        return df

    def del_stor(self):
        '''
        deletes the logger storage can't be undone!
        '''
        tg = telegram.createTG(self.ser, self.address, 'C.ALL')
        telegram.checkRe(tg)
    
    def read_channel(self, channelNr):
        '''
        reads a specific channel on the logger
        channelNr must be type str and must have the format '01'-'20' or '80'-'BB'
        '''
        tg = telegram.createTG(self.ser, self.address, 'R', channelNr)
        tg = tg.decode('ascii')[1:]
        return tg

    def read_datetime(self):
        '''
        reads the current logger time
        returns the time as datetime object
        '''
        tg = telegram.createTG(self.ser, self.address, 'H')
        tg = tg.decode('ascii')[1:-1]
        tg = datetime.strptime(tg, '%y%m%d%H%M%S')
        return tg

    def set_datetime(self, newTime = datetime.now()):
        '''
        newTime = time to set the logger clock to. Default is the system time
        else newTime must be a datetime object
        '''
        newTime       = datetime.strftime(newTime, '%y%m%d%H%M%S')
        tg            = telegram.createTG(self.ser, self.address, 'G', newTime)
        telegram.checkRe(tg)
    
    def other_call(self, *argv):
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
