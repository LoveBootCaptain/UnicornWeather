#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is for testing and not finished yet.
"""

import scrollphat
from PIL import Image

from modules.Config import LOW


class Display(object):
    def __init__(self, display, brightness, thing):
        self.display = display()
        self.brightness = self.display.set_brightness(brightness)
        if thing == str:
            self.thing = thing
        if isinstance(Image, thing):
            self.thing = Image.open(thing)


if __name__ == '__main__':

    scroll = Display(scrollphat, LOW.scrollphat, 'hello')

    print(scroll.__dict__)
