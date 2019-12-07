# Script for reading the data from Theodor Friedrich's Combilog 1022 via ascii
# to computer connected via USB e.g. a raspberry pi or other mini computer that is able
# to run python3
# Github: theendlessriver13/combilog1022
# (C) Jonas Kittner 2019

# Imports
import pandas       as pd
from   serial       import Serial, EIGHTBITS, PARITY_NONE
from   combilog_FUN import combilog
from   datetime     import datetime

# set up port and connection
ser          = Serial()
ser.baudrate = 9600
ser.port     = 'com3' #'/dev/ttyACM0'
ser.bytesize = EIGHTBITS
ser.parity   = PARITY_NONE
ser.timeout  = 1

# set up logger params
mylogger_params = {
    'address': '01',
    'passwd': 'your_password',
    'ser': ser,
    'cnames': ['name',
        'timedate', 
        'airtemp2m',
        'relhum',
        'winvel',
        'gusts',
        'soiltemp',
        'precip']
}

## Examples
## Read whole logger storage

# open port and set everything up for communication
ser.open()
print('Port open: ', ser.is_open)

# Define logger
mylogger = combilog(mylogger_params)

# authenticate when necessary
mylogger.auth()

# Set pointer to start of logger storage 
mylogger.pointer1_tostart()

# read all bookings from logger
logs = mylogger.read_bookings_pt1()

# Write logs to CSV
logs.to_csv('mylogger_data.csv', index = False)

## Read data starting from defined date
# set pointer to exact date and time
mylogger.pointer1_to_date(datetime.strptime('2019-11-23 23:50:00', '%Y-%m-%d %H:%M:%S'))

# read bookings from set pointer
logsDate = mylogger.read_bookings_pt1()

# write to csv
logsDate.to_csv('mylogger_data_date.csv', index = False)

## Logger info
# get nr of logs
print(mylogger.nr_logs())

## read value of one channel
print(mylogger.read_channel('04'))

## Logger time
# read logger time
print(mylogger.read_datetime())

# set logger to defined time
mylogger.set_datetime(datetime.strptime('2019-11-23 20:50:00', '%Y-%m-%d %H:%M:%S'))

# set logger time to system time
mylogger.set_datetime()

## Delete
# delete data storage on logger

#mylogger.del_stor()

# for any other calls as listed in the COMBILOG 1022 manual
# use method self.other_call() e.g.

# Device Infos
print(mylogger.other_call('V'))

# Channel infos from channel 4
print(mylogger.other_call('B', '04'))

# measuring intervall
print(mylogger.other_call('X'))

# close port
ser.close()
print('Port open: ', ser.is_open)