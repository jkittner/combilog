# Script for reading the data from Theodor Friedrich's Combilog 1022 via ascii
# to a computer connected via USB e.g. a raspberry pi
# or other mini computer that is able
# to run python3
# Github: theendlessriver13/combilog1022
# Jonas Kittner 2020
from serial import EIGHTBITS
from serial import PARITY_NONE
from serial import Serial

from combilog_FUN import combilog

# set up port and connection
ser          = Serial()
ser.baudrate = 9600
ser.port     = 'com3'  # or '/dev/ttyACM0'
ser.bytesize = EIGHTBITS
ser.parity   = PARITY_NONE
ser.timeout  = 1

# set up logger params
mylogger_params = {
    'address': '01',
    'passwd': 'your_password',
    'ser': ser,
    'cnames': [
        'name',
        'timedate',
        'airtemp2m',
        'relhum',
        'winvel',
        'gusts',
        'soiltemp',
        'precip',
    ],
}

# Examples
# open port and set everything up for communication
ser.open()
print('Port open: ', ser.is_open)

# Define logger
mylogger = combilog(mylogger_params)

# authenticate when necessary
mylogger.auth()

# Set pointer to start of logger storage
mylogger.pointer1_tostart()

# get nr of logs
print(mylogger.nr_logs())

# read all bookings from logger
logs = mylogger.read_bookings_pt1()

# Write logs to CSV
logs.to_csv('mylogger_data.csv', index=False)

# read logger time
print(mylogger.read_datetime())

# delete data storage on logger
mylogger.del_stor()

# for any other calls as listed in the COMBILOG 1022 manual
# use method .other_call() e.g.

ser.close()
print('Port open: ', ser.is_open)
