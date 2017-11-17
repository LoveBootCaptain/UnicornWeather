#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging.handlers
from datetime import datetime
from threading import Lock

lock_func = Lock()


PROJECT_PATH = '/home/pi/UnicornWeather/'
LOG_PATH = PROJECT_PATH + 'logs/new_debug.log'

# create a debug logger
DEBUG_LOG_FILENAME = LOG_PATH

# Set up a specific logger with our desired output level
debug_logger = logging.getLogger('DebugLogger')
debug_logger.setLevel(logging.DEBUG)

# Add the log message handler to the logger and make a log-rotation of 100 files with max. 10MB per file
debug_handler = logging.handlers.RotatingFileHandler(DEBUG_LOG_FILENAME, maxBytes=100000, backupCount=1)
debug_logger.addHandler(debug_handler)


def log_str(string):

    log_time = datetime.now().strftime("%m-%d-%Y-%H:%M:%S")
    new_log_str = '[{}] - {}'.format(log_time, string)
    print(new_log_str)
    debug_logger.debug(new_log_str)


if __name__ == '__main__':
    log_str('hello')

