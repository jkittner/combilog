# Downloading logged data from Theodor Friedrichs & Co Combilog 1022

## Intention for writing this code
The intention for writing this code was the lack of  affordable opportunities offered by Theodor Friedrichs for automatically downloading the data from the datalogger.
Also there still is no software for Linux or for servers without a GUI.
This script should run on all of them, they just need Python3.
This software should partitially do what the Comgraph software does which only runs on windows and is not free.


##### Disclaimer
I am not a professional programmer at all, but I try to do my best to get things running the way I want them to - and sometimes it even works! 
So feel free to copy my messy code and improve it until it suits your needs.

## Usage
The file `combilog_FUN.py` includes all the classes, functions, class objects and classmethods you will need to communicate with the logger.

The file `combilog_read_data.py` includes basic examples how to use the classes.

The class object `other_call`from the class `combilog` offers you the option to create any call as described in the logger manual using this class and the initialized logger. The commonly used calls have their own class object in the class `combilog`.

The manual can be found [here](http://www.th-friedrichs.de/assets/ProductPage/ProductDownload/E1022Datasheet.pdf). The `ASCII` protocol is described starting at page 118.

### My Usage
I personally use this for my private weatherstation. The logger is connected via USB to a Raspberry Pi running a basic rasbian. Every 5 minutes - when a log was written - I fetch the data from the logger and save it directly into a PostgreSQL database.
All other automated scripts get the latest data out of the database. The data analysis is done on the Pi and all plots are created using `R`.
All graphs are hosted on a website using `apache` on the Raspberry Pi.