#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from datetime import datetime
from threading import Thread

import blinkt

from modules.Config import *
from modules.Data import Data
from modules.Log import log_str


class Blinkt(object):

    brightness = LOW.blinkt
    brightness_setting = None

    def __init__(self):
        self.name = 'Blinkt'
        log_str('init {}'.format(self.__module__))

        self.leds = [0, 0, 0, 0, 0, 16, 64, 255, 64, 16, 0, 0, 0, 0, 0]
        self.animation_cycle_time = 0.25
        self.start_time = time.time()

        self.hour = int(datetime.now().strftime("%H"))

        if 9 <= self.hour <= 17:
            self.brightness = HIGH.blinkt
            self.brightness_setting = 'day'

        elif 18 <= self.hour <= 23 or 0 <= self.hour <= 8:
            self.brightness = LOW.blinkt
            self.brightness_setting = 'night'

        else:
            self.brightness = self.brightness

        log_str('blinkt brightness: {} - {}: {}'.format(self.brightness, self.brightness_setting, self.hour))
        blinkt.set_brightness(self.brightness)

    @staticmethod
    def fade():
        blinkt.show()
        time.sleep(0.075)

    def clear(self, fast):
        log_str('clear blinkt')

        if not fast:
            for i in reversed(range(8)):
                blinkt.set_pixel(i, 0, 0, 0)
                self.fade()

        blinkt.clear()
        blinkt.show()

    def show_graph(self, forecast_list=TEST_FORECAST):

        self.clear(False)

        for position, item in enumerate(forecast_list):

            if item == 'G':
                blinkt.set_pixel(position, 0, 255, 0)
                self.fade()
            elif item == 'Y':
                blinkt.set_pixel(position, 255, 175, 0)
                self.fade()
            elif item == 'O':
                blinkt.set_pixel(position, 255, 50, 0)
                self.fade()
            elif item == 'R':
                blinkt.set_pixel(position, 255, 0, 0)
                self.fade()
            else:
                blinkt.set_pixel(position, 0, 0, 0)
                self.fade()

        blinkt.show()

    def led_loop(self):

        self.show_graph(Data().get_rain_forecast())

        time.sleep(20)

        t = Thread(target=Blinkt().led_loop, daemon=True)
        THREADS.append(t)
        t.start()


if __name__ == '__main__':
    myBlinkt = Blinkt()
    myBlinkt.show_graph()

