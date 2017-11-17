#!/usr/bin/python3
# -*- coding: utf-8 -*-
from collections import namedtuple


RUNNING = True

TIMEFORMAT = '%H:%M'

THREADS = []
TIMER = []

API_ENDPOINT = 'http://192.168.178.123/latest_weather.json'

PROJECT_PATH = '/home/pi/UnicornWeather/'
DATA_PATH = PROJECT_PATH + 'logs/latest_weather.json'

ICON_PATH = PROJECT_PATH + 'icons/'
ICON_EXTENSION = '.png'

TEST_IMAGE = ICON_PATH + 'raspberry' + ICON_EXTENSION
TEST_STRING = '????'
TEST_FORECAST = ['G', 'G', 'Y', 'Y', 'O', 'O', 'R', 'R']

BLINKT_BRIGHTNESS = 0.05
BLINKT_FADE_TIME = 0.05
BLINKT_LEDS = 8

UNICORN_ROTATION = 90

SCROLL_ROTATION = False


BRIGHTNESS = namedtuple('BRIGHTNESS', ['unicorn', 'scrollphat', 'blinkt'])

LOW = BRIGHTNESS(0.45, 3, 0.033)
MID = BRIGHTNESS(0.6, 7, 0.06)
HIGH = BRIGHTNESS(0.75, 10, 0.08)
ULTRA = BRIGHTNESS(1, 55, 0.25)


# def set_brightness(device):
#
#     brightness = None
#
#     hour = int(datetime.datetime.now().strftime("%H"))
#
#     if 0 <= hour <= 8:
#         brightness = LOW.scrollphat
#
#
#     try:
#
#         if device == 'scrollphat':
#             brightness = LOW.scrollphat
#
#         elif device == 'unicorn':
#             brightness = LOW.unicorn
#
#     finally:
#         return brightness
