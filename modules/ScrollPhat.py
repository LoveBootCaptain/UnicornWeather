#!/usr/bin/python3f
# -*- coding: utf-8 -*-
from datetime import datetime
from threading import Thread
from time import sleep

import scrollphat

from modules.Config import *
from modules.Data import Data
from modules.Log import log_str


class ScrollPhat(object):

    brightness = LOW.scrollphat
    brightness_setting = None
    rotation = SCROLL_ROTATION

    def __init__(self):

        self.name = 'ScrollPhat'
        log_str('init {}'.format(self.__module__))

        self.rotation = SCROLL_ROTATION

        scrollphat.set_rotate(self.rotation)

        self.hour = int(datetime.now().strftime("%H"))

        if 9 <= self.hour <= 17:
            self.brightness = HIGH.scrollphat
            self.brightness_setting = 'day'

        elif 18 <= self.hour <= 23 or 0 <= self.hour <= 8:
            self.brightness = LOW.scrollphat
            self.brightness_setting = 'night'

        else:
            self.brightness = self.brightness

        log_str('scrollphat brightness: {} - {}: {}'.format(self.brightness, self.brightness_setting, self.hour))
        scrollphat.set_brightness(self.brightness)

    @classmethod
    def set_scroll_brightness(cls, level=brightness):

        cls.brightness = level

        log_str('set scrollphat brightness: {}'.format(cls.brightness))
        scrollphat.set_brightness(cls.brightness)

        return cls.brightness

    @staticmethod
    def show_str(string=TEST_STRING):

        log_str(string)

        scrollphat.clear_buffer()
        scrollphat.write_string(string)

    def scroll(self, string=TEST_STRING):

        self.show_str(string)

        length = scrollphat.buffer_len()

        for i in range(length):

            scrollphat.scroll()
            sleep(0.1)

    def str_loop(self):

        string = Data().output_str()

        self.scroll(string)

        sleep(10)

        t = Thread(target=ScrollPhat().str_loop, daemon=True)
        THREADS.append(t)
        t.start()

    def clear(self, fast=False):
        log_str('clear scroll')

        if not fast:
            for x in range(11):
                for y in range(5):
                    scrollphat.set_pixel(x, y, 0)
                    sleep(0.015)
                    scrollphat.update()

        scrollphat.clear_buffer()
        scrollphat.clear()
        scrollphat.update()


if __name__ == '__main__':

    ScrollPhat().scroll(Data().output_str())
