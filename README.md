[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![test coverage](https://img.shields.io/badge/coverage-94%25-green)](#Tests)
# combilog
A tool to interact with the combilog datalogger by Theodor Friedrichs. Currently only the combilog 1022 is supported.
## Installation
`pip install combilog`
## Usage
### Read the logger and save as csv
```py
import combilog
import csv

# initialize a `combilog` object
my_log = combilog.Combilog(logger_addr=1, port='com3')
# authenticate if needed
my_log.authenticate(passwd='12345678')
# set pointer 1 to the start of the memory to read the logger
my_log.pointer_to_start(pointer=1)
# read the logger specify wich pointer to use
logs = my_log.read_logger(pointer=1, verbose=True, output_type='list')

# export as csv
with open('logs.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    # write header
    HEADER = ['timestamp', 'channel_1', 'channel_2', ..., 'channel_n']
    writer.writerow(HEADER)
    for i in logs:
        writer.writerow(i)

```
### Read the logger and assign to a pandas DataFrame
```py
import combilog
import pandas as pd

# initialize a `combilog` object
my_log = combilog.Combilog(logger_addr=1, port='com3')
# authenticate if needed
my_log.authenticate(passwd='12345678')
# set pointer 1 to the start of the memory to read the logger
my_log.pointer_to_start(pointer=1)
# read the logger specify wich pointer to use. output_type is `dict` for
# the pandas dataframe
logs = my_log.read_logger(pointer=1, verbose=True, output_type='dict')

df = pd.DataFrame.from_dict(data=logs, orient='index')

print(df.head(3))
```
### Finding the right port

- On Linux you can check for the used port using dmesg | grep -E 'tty|usb'
- you are likely to see something like this at the bottom:
```
[202789.491199] usb 1-1.1.2: New USB device found, idVendor=eb03, idProduct=0920, bcdDevice= 1.10
[202789.491213] usb 1-1.1.2: New USB device strings: Mfr=1, Product=2, SerialNumber=0
[202789.491223] usb 1-1.1.2: Product: CombiLog 1022
[202789.491232] usb 1-1.1.2: Manufacturer: Th.-Friedrichs
[202789.640236] cdc_acm 1-1.1.2:1.0: ttyACM0: USB ACM device
```
- Your port is `ttyACM0`
- On windows simply check the device-manager for a com port

### Notes
- The logger manual can be found [here](http://www.th-friedrichs.de/assets/ProductPage/ProductDownload/ManualE1022V109.pdf). The `ASCII` protocol this package uses is described starting at page 118.
- Sometimes setting the pointer fails the first time and it is successful the second time, so a e.g. `@retry` decorator might be useful
## My Usage
I personally use this for my private weatherstation. The logger is connected via USB to a Raspberry Pi running a basic rasbian. Every 5 minutes when a log was written I fetch the data from the logger and save it directly to PostgreSQL database.

## Why should I use this code?
The intention for writing this code was the lack of affordable options offered by Theodor Friedrichs for automatically downloading the data from the datalogger.
Also there still is no software for Linux or for servers without a GUI.
This script should run on all of them, they just need python3.
This software should do what the automatic part of the expensive Comgraph software does which only runs on windows and is obviously not free.


## Tests
- Most of the tests unfortunatelly depend on a logger beeing connected to `com3`.
- The tests were ran using a `Combilog 1022` with `hw_version` = `V4.01` and `sw_revision` = `2.26`
- The logger settings used for testing can be found in `testing/tetsing.PRO`
- the requirements for testing in `requirements-dev.txt`
- the test coverage is not 100 % because some exceptions cannot be triggered manually and also the transparent mode cannot be tested since no logger network is available for testing.

```console
----------- coverage: platform win32, python 3.7.7-final-0 -----------
Name          Stmts   Miss  Cover
---------------------------------
combilog.py     309     18    94%
```
