#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import threading
import time
import json

import requests
import unicornhat as unicorn
import blinkt
import scrollphat

from PIL import Image
from sys import argv
import logging.handlers

leds = [0, 0, 0, 0, 0, 16, 64, 255, 64, 16, 0, 0, 0, 0, 0]

animation_cycle_time = 0.25

width, height = unicorn.get_shape()

CONNECTION_ERROR = False
REFRESH_ERROR = False

PATH_VALID = False

threads = []

ICON_PATH = 'icons/'
icon_extension = '.png'

WeatherIcon_Path = ''

api_endpoint = 'http://192.168.178.123/'
latest = 'latest_weather.json'
current = 'current_weather.json'

running = True

color_list = []
forecast_range_hour = 8  # use len(hourly) for full data (48h)

start_time = time.time()

# create a debug logger

debug_path = 'logs/Debug_Log.log'
DEBUG_LOG_FILENAME = debug_path

# Set up a specific logger with our desired output level
debug_logger = logging.getLogger('DebugLogger')
debug_logger.setLevel(logging.DEBUG)

# Add the log message handler to the logger and make a log-rotation of 100 files with max. 10MB per file
debug_handler = logging.handlers.RotatingFileHandler(DEBUG_LOG_FILENAME, maxBytes=100000, backupCount=1)
debug_logger.addHandler(debug_handler)


def log_string(string):
    print(string)
    debug_logger.debug(string)


def scroll_init():
    scrollphat.set_brightness(10)
    scrollphat.set_rotate(False)


def scroll_clear():
    scrollphat.clear()
    scrollphat.update()


def blinkt_fade():
    blinkt.show()
    time.sleep(0.05)


def blinkt_clear():
    for i in reversed(range(8)):
        blinkt.set_pixel(i, 0, 0, 0)
        blinkt_fade()

    blinkt.clear()


def blinkt_init():
    blinkt.set_brightness(0.05)


def unicorn_init():
    unicorn.brightness(0.75)
    unicorn.rotation(90)


def unicorn_clear():
    unicorn.clear()
    unicorn.show()


def clear_all():
    unicorn_clear()
    blinkt_clear()
    scroll_clear()


def quit_all():
    global running

    running = False

    for thread in threads:
        thread.cancel()
        thread.join()

    clear_all()

    quit()


def blinkt_color(color):
    blinkt_clear()

    for y in range(9):

        delta = (time.time() - start_time) * 16

        # Triangle wave, a snappy ping-pong effect
        offset = int(abs((delta % 16) - 8))

        if color == 'white':

            for i in range(8):
                blinkt.set_pixel(i, leds[offset + i], leds[offset + i], leds[offset + i])

            blinkt.show()

        elif color == 'red':

            for i in range(8):
                blinkt.set_pixel(i, leds[offset + i], 0, 0)

            blinkt.show()

        elif color == 'yellow':

            for i in range(8):
                blinkt.set_pixel(i, leds[offset + i], leds[offset + i], 0)

            blinkt.show()

        elif color == 'blue':

            for i in range(8):
                blinkt.set_pixel(i, 0, 0, leds[offset + i])

            blinkt.show()

        elif color == 'green':

            for i in range(8):
                blinkt.set_pixel(i, 0, leds[offset + i], 0)

            blinkt.show()

        else:

            log_string('ERROR: Blinkt Color {} not set. Showing white.'.format(color))

            for i in range(8):
                blinkt.set_pixel(i, leds[offset + i], leds[offset + i], leds[offset + i])

            blinkt.show()

        time.sleep(0.1)

    blinkt.clear()
    blinkt.show()

    log_string('Blinkt: {}'.format(color))


def update_json():

    global CONNECTION_ERROR

    try:

        log_string('trying contact url: {}'.format(api_endpoint + latest))

        connection = requests.get(api_endpoint + latest, timeout=2)
        data = connection.json()

        CONNECTION_ERROR = False

        log_string('status: {} | url: {}'.format(connection.status_code, connection.url))
        log_string('Update done!')

        with open('logs/latest_weather.json', 'w') as outputfile:
            json.dump(data, outputfile, indent=2, sort_keys=True)

        log_string('json file saved')

        blinkt_color('green')

        time.sleep(0.5)

    except Exception as e:

        CONNECTION_ERROR = True

        log_string('ERROR: {}'.format(e))

        quit_all()


def read_json():
    global REFRESH_ERROR

    data = open('logs/latest_weather.json').read()

    temp_data = json.loads(data)

    log_string('json data read by module')

    return temp_data


def icon_path():

    global WeatherIcon_Path, PATH_VALID

    # known conditions:
    # clear-day, clear-night, partly-cloudy-day, partly-cloudy-night, wind, cloudy, rain, snow, fog

    try:

        icon = read_json()['currently']['icon']
        log_string('icon found: {}'.format(icon))

        WeatherIcon_Path = ICON_PATH + icon + icon_extension

        log_string('validating path: {}'.format(WeatherIcon_Path))

        if os.path.isfile(WeatherIcon_Path):

            log_string('TRUE: {}'.format(WeatherIcon_Path))
            PATH_VALID = True

            blinkt_clear()

            blinkt_color('red')

            time.sleep(0.5)

            return WeatherIcon_Path

        else:

            log_string('FALSE: {}'.format(WeatherIcon_Path))
            PATH_VALID = False

            quit_all()

    except TypeError as e:

        log_string('no data found - quit')
        log_string('ERROR: {}'.format(e))

        quit_all()


def get_temp():

    temp = read_json()['currently']['sensor_temp_outside']
    temp_str = str("{}'".format(int(temp)))
    log_string('Temp: {}'.format(temp_str))
    scrollphat.write_string(temp_str)
    scrollphat.update()

    blinkt_color('blue')

    time.sleep(0.5)


def get_rain_forecast():

    percentage_list = []
    color = False

    global color_list

    color_list = []

    hourly_data = read_json()['hourly']['data']

    for item in hourly_data:
        rain_percentage = item['precipProbability'] * 100
        percentage_list.append(round(rain_percentage))

    for percentage in percentage_list[:forecast_range_hour]:

        if percentage == 0:
            color = "G"  # GREEN
        elif 0 < percentage <= 15:
            color = "Y"  # YELLOW
        elif 16 < percentage <= 30:
            color = "O"
        elif 31 <= percentage <= 100:
            color = "R"  # RED

        color_list.append(color)

    log_string('Regenwahrscheinlichkeit 24h: {}\n'
               'Farben auf Display: {}'.format(
                percentage_list[:forecast_range_hour],
                color_list
                ))

    show_graph(color_list)


def show_graph(forecast_list):

    for position, item in enumerate(forecast_list):

        if item == 'G':
            blinkt.set_pixel(position, 0, 255, 0)
            blinkt_fade()
        elif item == 'Y':
            blinkt.set_pixel(position, 255, 175, 0)
            blinkt_fade()
        elif item == 'O':
            blinkt.set_pixel(position, 255, 50, 0)
            blinkt_fade()
        elif item == 'R':
            blinkt.set_pixel(position, 255, 0, 0)
            blinkt_fade()


def draw_animation(image):
    # this is the original pimoroni function for drawing sprites
    try:

        for o_x in range(int(image.size[0] / width)):

            for o_y in range(int(image.size[1] / height)):

                valid = False

                for x in range(width):

                    for y in range(height):

                        pixel = image.getpixel(((o_x * width) + y, (o_y * height) + x))
                        r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])

                        if r or g or b:
                            valid = True

                        unicorn.set_pixel(x, y, r, g, b)

                if valid:
                    unicorn.show()
                    # scrollphat.scroll()
                    time.sleep(animation_cycle_time)

    except KeyboardInterrupt:

        quit_all()
        unicorn.off()


def draw_single_icon(animation):
    unicorn.clear()

    single_file = ICON_PATH + animation + icon_extension

    log_string('Start drawing single icon or animation: {}'.format(animation))

    img = Image.open(single_file)

    draw_animation(img)


def update_unicorn():
    unicorn.clear()

    log_string('Start Unicorn image loop')

    while running:

        img = Image.open(WeatherIcon_Path)

        draw_animation(img)

    else:

        log_string('Something went wrong while picking up the img')

        quit_all()


def update():

    update_thread = threading.Timer(60, update)
    update_thread.start()
    threads.append(update_thread)

    blinkt_clear()
    update_json()


def loop():

    loop_thread = threading.Timer(30, loop)
    loop_thread.start()
    threads.append(loop_thread)

    blinkt_clear()
    icon_path()
    get_temp()
    get_rain_forecast()


def main():
    global running

    try:

        update()
        loop()

    except KeyboardInterrupt:

        running = False

        quit_all()


def test_unicorn():
    log_string('Testing all images in folder {}'.format(ICON_PATH))

    for image in os.listdir(ICON_PATH):

        if image.endswith(icon_extension):

            log_string('Testing image: {}'.format(ICON_PATH + image))

            img = Image.open(ICON_PATH + image)

            draw_animation(img)

        else:

            log_string('Not using this file, not an image: {}'.format(image))

    unicorn.clear()
    unicorn.show()


if __name__ == '__main__':

    log_string('\n *** starting UnicornPi *** \n')

    try:

        blinkt_init()
        unicorn_init()
        scroll_init()

        if argv[1] == 'test':

            log_string('testing animations and images')

            # get_rain_forecast()
            # show_graph(get_rain_forecast())
            # draw_single_icon('partly-cloudy-day')
            test_unicorn()

        elif argv[1] == 'run':

            log_string('booting weather station')

            draw_single_icon('raspberry_boot')

            main()

            update_unicorn()

        elif argv[1] == 'clear':

            clear_all()

    except KeyboardInterrupt:

        running = False

        quit_all()
