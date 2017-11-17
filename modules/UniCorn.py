#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from threading import Thread
from time import sleep

import unicornhat as unicorn
from PIL import Image

from modules.Config import *
from modules.Data import Data
from modules.Log import log_str
from modules.Blinkt import Blinkt


class UniCorn(object):

    brightness = LOW.unicorn
    brightness_setting = None
    rotation = UNICORN_ROTATION

    def __init__(self):

        self.name = 'UniCorn'
        log_str('init {}'.format(self.__module__))

        self.rotation = UNICORN_ROTATION

        unicorn.rotation(self.rotation)

        self.hour = int(datetime.now().strftime("%H"))

        if 9 <= self.hour <= 17:
            self.brightness = HIGH.unicorn
            self.brightness_setting = 'day'

        elif 18 <= self.hour <= 23 or 0 <= self.hour <= 8:
            self.brightness = LOW.unicorn
            self.brightness_setting = 'night'

        else:
            self.brightness = self.brightness

        log_str('unicorn brightness: {} - {}: {}'.format(self.brightness, self.brightness_setting, self.hour))
        unicorn.brightness(self.brightness)

    @classmethod
    def set_unicorn_brightness(cls, level=brightness):

        cls.brightness = level

        log_str('unicorn brightness: {}'.format(cls.brightness))
        unicorn.brightness(cls.brightness)

        return cls.brightness

    @staticmethod
    def draw_animation(image=Image.open(TEST_IMAGE)):

        width, height = unicorn.get_shape()

        # this is the original pimoroni function for drawing sprites

        log_str('start image loop')

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
                    sleep(0.25)

        log_str('image loop done')

    def icon_loop(self):
        image = Data().image()

        self.draw_animation(Image.open(image))

        t = Thread(target=UniCorn().icon_loop, daemon=True)
        THREADS.append(t)
        t.start()

    @staticmethod
    def clear():
        log_str('clear unicorn')
        unicorn.clear()
        unicorn.show()
        unicorn.off()


if __name__ == '__main__':

    myUniCorn = UniCorn()

    myUniCorn.icon_loop()
