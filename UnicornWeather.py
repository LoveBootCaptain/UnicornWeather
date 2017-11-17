#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import logging.handlers
import multiprocessing
import os
import threading
import time
from sys import argv, exit

import blinkt
import requests
import scrollphat
import unicornhat as unicorn
from PIL import Image

leds = [0, 0, 0, 0, 0, 16, 64, 255, 64, 16, 0, 0, 0, 0, 0]

animation_cycle_time = 0.25

width, height = unicorn.get_shape()

CONNECTION_ERROR = False
REFRESH_ERROR = False

PATH_VALID = False

threads = []

ICON_PATH = 'icons/'
icon_extension = '.png'

WeatherIcon_Path = ICON_PATH + 'raspberry' + icon_extension

api_endpoint = 'http://192.168.178.123/'
latest = 'latest_weather.json'
current = 'current_weather.json'

running = True

color_list = []
forecast_range_hour = 8  # use len(hourly) for full data_loop (48h)

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
    scrollphat.set_brightness(25)
    scrollphat.set_rotate(False)


def scroll_clear():
    scrollphat.clear_buffer()
    scrollphat.clear()
    scrollphat.update()


def blinkt_init():
    blinkt.set_brightness(0.05)


def blinkt_fade():
    blinkt.show()
    time.sleep(0.05)


def blinkt_clear():
    for i in reversed(range(8)):
        blinkt.set_pixel(i, 0, 0, 0)
        blinkt_fade()

    blinkt.clear()


def unicorn_init():
    unicorn.brightness(0.75)
    unicorn.rotation(90)


def unicorn_clear():
    unicorn.clear()
    unicorn.show()


def clear_all():

    log_string('\n *** clearing all displays *** \n')

    scroll_clear()
    unicorn_clear()
    blinkt_clear()


def quit_all():

    log_string('Quit now')

    global running

    running = False

    for thread in threads:
        thread.cancel()
        thread.join()

    clear_all()


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

        connection = requests.get(api_endpoint + latest, timeout=15)
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

    log_string('json data_loop read by module')

    return temp_data


def update_icon_path():

    global WeatherIcon_Path, PATH_VALID

    # known conditions:
    # clear-day, clear-night, partly-cloudy-day, partly-cloudy-night, wind, cloudy, rain, snow, fog

    try:

        icon = read_json()['currently']['icon']
        log_string('icon found: {}'.format(icon))

        if os.path.isfile(WeatherIcon_Path):

            log_string('TRUE valid path: {}'.format(WeatherIcon_Path))
            PATH_VALID = True

            WeatherIcon_Path = ICON_PATH + icon + icon_extension

            blinkt_color('red')

            time.sleep(0.5)

        else:

            log_string('FALSE: {}'.format(WeatherIcon_Path))
            PATH_VALID = False

            quit_all()

    except TypeError as e:

        log_string('no data_loop found - quit')
        log_string('ERROR: {}'.format(e))

        quit_all()


def get_temp_str():

    temp = read_json()['currently']['sensor_temp_outside']
    temp_str = str("{}'".format(int(temp))).zfill(3)
    log_string('Temp: {}'.format(temp_str))

    return temp_str


def get_time_str():

    time_str = str(time.strftime('%H:%M'))
    log_string(time_str)

    return time_str


def get_summary_str():

    summary_str = read_json()['currently']['summary_str']

    replace_me = {
        'ö': 'oe',
        'Ö': 'Oe',
        'ü': 'ue',
        'Ü': 'Ue',
        'ä': 'ae',
        'Ä': 'Ae',
        'ß': 'ss'
    }

    for key in replace_me:

        summary_str = summary_str.replace(key, replace_me[key])

    log_string('summary_str: {} '.format(summary_str))

    return summary_str


def build_scroll_str():

    tmp_str = get_temp_str()
    summary_str = get_summary_str()
    time_str = get_time_str()

    scroll_str = str(tmp_str + ' ' + summary_str + ' ' + time_str + ' ')

    log_string(scroll_str)

    return scroll_str


def scroll():

    if running:

        scrollphat.clear_buffer()
        scrollphat.write_string(build_scroll_str())

        length = scrollphat.buffer_len()

        for i in range(length):
            try:
                scrollphat.scroll()
                time.sleep(0.1)
            except KeyboardInterrupt:
                quit_all()
    else:

        quit_all()


def get_rain_forecast():

    percentage_list = []
    color = False

    global color_list

    color_list = []

    hourly_data = read_json()['hourly']['data_loop']

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

    log_string('Regenwahrscheinlichkeit 8h: {}\n'
               'Farben auf Display: {}'.format(
                percentage_list[:forecast_range_hour],
                color_list
                ))

    show_graph(color_list)


def show_graph(forecast_list):

    if running:

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
            else:
                blinkt.set_pixel(position, 0, 0, 0)
                blinkt_fade()

    else:

        quit_all()


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

    global WeatherIcon_Path

    unicorn.clear()

    log_string('Start Unicorn image loop')

    while running:

        img = Image.open(WeatherIcon_Path)

        draw_animation(img)

    else:

        log_string('Something went wrong while picking up the img')

        quit_all()


def update():

    update_thread = threading.Timer(90, update)
    update_thread.start()
    threads.append(update_thread)

    if running:

        blinkt_clear()
        update_json()
        get_rain_forecast()

    else:

        quit_all()


def loop():

    loop_thread = threading.Timer(30, loop)
    # loop_thread.daemon = True
    loop_thread.start()
    threads.append(loop_thread)

    if running:

        blinkt_clear()
        multiprocessing.Process(target=scroll).start()
        blinkt_color('blue')
        time.sleep(0.5)
        update_icon_path()
        get_rain_forecast()

    else:

        quit_all()


def main():
    global running

    log_string('booting weather station')

    try:

        draw_single_icon('raspberry_boot')
        update()
        loop()
        update_unicorn()

    except KeyboardInterrupt:

        running = False

        quit_all()


def test_unicorn():
    log_string('Testing all images in folder {}'.format(ICON_PATH))
    log_string(", ".join(sorted(os.listdir(ICON_PATH))))

    for image in sorted(os.listdir(ICON_PATH)):

        if image.endswith(icon_extension):

            log_string('Testing image: {}'.format(ICON_PATH + image))

            img = Image.open(ICON_PATH + image)

            draw_animation(img)

        else:

            log_string('Not using this file, not an image: {}'.format(image))

    unicorn.clear()
    unicorn.show()


if __name__ == '__main__':

    try:

        blinkt_init()
        unicorn_init()
        scroll_init()

        if argv[1] == 'icon_test':

            log_string('\n *** testing animations and images *** \n')

            # get_rain_forecast()
            # show_graph(get_rain_forecast())
            # draw_single_icon('partly-cloudy-day')
            test_unicorn()
            quit_all()

        elif argv[1] == 'run':

            log_string('\n *** starting UnicornPi *** \n')
            main()

        elif argv[1] == 'clear':

            clear_all()

    except KeyboardInterrupt:

        running = False

        quit_all()
