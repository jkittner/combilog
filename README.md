# Downloading logged data from Theodor Friedrichs & Co Combilog 1022

## Usage
The file `combilog_FUN.py` includes all classes you will need to communicate with the logger.

The file `combilog_read_data.py` includes basic examples how to use the classes.

The class object `other_call` from the class `combilog` offers you the option to create any call as described in the logger manual using this class and the initialized logger. The commonly used calls have their own class object in the class `combilog`.

The manual can be found [here](http://www.th-friedrichs.de/assets/ProductPage/ProductDownload/ManualE1022V109.pdf). The `ASCII` protocol is described starting at page 118.

### My Usage
I personally use this for my private weatherstation. The logger is connected via USB to a Raspberry Pi running a basic rasbian. Every 5 minutes when a log was written I fetch the data from the logger and save it directly into a PostgreSQL database.

### Intention for writing this code
The intention for writing this code was the lack of affordable opportunities offered by Theodor Friedrichs for automatically downloading the data from the datalogger.
Also there still is no software for Linux or for servers without a GUI.
This script should run on all of them, they just need python3.
This software should do what the autmatic part of the Comgraph software does which only runs on windows and is not free.