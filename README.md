[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
# Downloading logged data from Theodor Friedrichs & Co Combilog 1022

## Usage
The file `combilog_FUN.py` includes all classes you will need to communicate with the logger.
### Initial setup of your script

1. Import the class combilog to your file
    ```python
    from combilog_FUN import combilog
    ```
1. Set up the serial connection to your logger
    ```python
    from serial import EIGHTBITS
    from serial import PARITY_NONE
    from serial import Serial

    ser          = Serial()
    ser.baudrate = 9600
    ser.port     = 'com3'  # or '/dev/ttyACM0'
    ser.bytesize = EIGHTBITS
    ser.parity   = PARITY_NONE
    ser.timeout  = 1
    ```
    - Specify the baudrate set in the logger's settings
    - Select the port where the logger is connected to
    - On Linux you can check for the used port using `dmesg | grep -E 'tty|usb'`
    - you are likely to see something like this at the bottom:
    ```
    [202789.491199] usb 1-1.1.2: New USB device found, idVendor=eb03, idProduct=0920, bcdDevice= 1.10
    [202789.491213] usb 1-1.1.2: New USB device strings: Mfr=1, Product=2, SerialNumber=0
    [202789.491223] usb 1-1.1.2: Product: CombiLog 1022
    [202789.491232] usb 1-1.1.2: Manufacturer: Th.-Friedrichs
    [202789.640236] cdc_acm 1-1.1.2:1.0: ttyACM0: USB ACM device
    ```
    - Your port is `ttyACM0`
    - On windows simply check the device-manager for a `com` port
    - Set the other variables `bytesize`, `parity` as specified in you logger's settings
    - Set a timeout for the calls
1. Set up the script with your logger's configuration
    - Fill in the dictionary with information about your logger
    ```python
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
    ```
    - Fill in `address` with the address specified in the logger's settings. It must be `2 char` wide
    - When you set a password to your logger, put it into `passwd` else just use an empty string `''`
    - `ser` must be type `serial.Serial` and should be the `ser` objected that was created before
    - Specify the names of the logged channels as a list in the order they appear when you read out your logger using the `combilog` Software
### Communicate with the logger
1. Define your logger
    ```python
    mylogger = combilog(mylogger_params)
    ```

1. Open the serial port
    ```python
    ser.open()
    ```
1. Authenticate when needed
    ```python
    mylogger.auth()
    ```
1. Set the pointer to the beginning
    ```python
    mylogger.pointer1_tostart()
    ```
1. Read all bookings using
    ```python
    logs = mylogger.read_bookings_pt1()
    ```
1. Save as csv file
    ```python
    logs.to_csv('mylogger_data.csv', index=False)
    ```
1. Delete the storage **cannot be undone!**
    ```python
    mylogger.del_stor()
    ```
1. close the serial connection
    ```python
    ser.close()
    ```

## Example
The file `combilog_read_data.py` includes a basic example that should work for you after entering the correct settings as described [here](### Initial setup of your script)
The example will:
- Authenticate using the specified password
- Set the pointer to the start
- Print out the number of logs tha are available
- Read all bookings to a variable called `logs`
- Export the readings to a csv-file named `mylogger_data.csv`
- Print out the current logger dat and time
- **Delete** the logger's storage

## Notes
- The method `other_call` from the class `combilog` offers you the option to create any call as described in the logger manual using this class and the initialized logger. The commonly used calls have their own method in the class `combilog`. It is most likely that the returned `str` of `other_call` needs further processing.
The manual can be found [here](http://www.th-friedrichs.de/assets/ProductPage/ProductDownload/ManualE1022V109.pdf). The `ASCII` protocol is described starting at page 118.
- Sometimes setting the pointer fails the first time. It is successful the second time.
## My Usage
I personally use this for my private weatherstation. The logger is connected via USB to a Raspberry Pi running a basic rasbian. Every 5 minutes when a log was written I fetch the data from the logger and save it directly to PostgreSQL database.

## Why should I use this code?
The intention for writing this code was the lack of affordable options offered by Theodor Friedrichs for automatically downloading the data from the datalogger.
Also there still is no software for Linux or for servers without a GUI.
This script should run on all of them, they just need python3.
This software should do what the automatic part of the expensive Comgraph software does which only runs on windows and is obviously not free.
