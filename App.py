#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import threading
import time

import atexit

from modules.Config import *
from modules.Data import Data
from modules.Log import log_str
from modules.ScrollPhat import ScrollPhat
from modules.UniCorn import UniCorn
from modules.Update import Update
from modules.Blinkt import Blinkt


class App(object):

    def __init__(self):
        self.name = 'myApp'
        log_str('init {}'.format(self.name))
        self.running = True
        atexit.register(self.stop)

    def start(self):

        log_str('start {}'.format(self.name))
        log_str('still alive {}'.format(self.running))

        # do init stuff here

        self.clear_all()

        Blinkt().show_graph()
        ScrollPhat().show_str()
        UniCorn().draw_animation()

        try:
            # start all loops

            log_str('still alive {}'.format(self.running))

            Update().data_loop()

            ScrollPhat().show_str(Data().output_str())

            Blinkt().show_graph(Data().get_rain_forecast())

            UniCorn().icon_loop()
            log_str('after the image loop')

            Blinkt().led_loop()
            log_str('after the led loop')

            ScrollPhat().str_loop()
            log_str('after the scroll loop')

            while self.running:
                time.sleep(1)
                log_str('still alive {}'.format(self.running))

            log_str('still alive {}'.format(self.running))

        except KeyboardInterrupt:

            log_str('*** quit: {}'.format(self.name))

            atexit._run_exitfuncs()

    def stop(self):
        log_str('stop {}'.format(self.name))
        self.quit_all()

    def quit_all(self):
        log_str('kill all timers')

        try:
            for timer in TIMER:
                timer.cancel()
        finally:
            self.clear_all()

    def run(self):
        log_str('run {}'.format(self.name))
        self.start()

    def clear_all(self):
        log_str('clear all {}'.format(self.name))
        UniCorn().clear()
        ScrollPhat().clear()
        Blinkt().clear()


if __name__ == '__main__':

    if sys.argv[1] == 'icon_test':
        pass

    elif sys.argv[1] == 'run':

        t = threading.Thread(target=App().run(), daemon=True)
        THREADS.append(t)
        t.start()

    elif sys.argv[1] == 'clear':

        App().stop()

    else:
        pass