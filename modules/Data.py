#!/usr/bin/python3
# -*- coding: utf-8 -*-
from json import load
from os import path
from time import strftime

from modules.Config import *
from modules.Log import lock_func, log_str


class Data(object):

    replace_me = {
        'ö': 'oe',
        'Ö': 'Oe',
        'ü': 'ue',
        'Ü': 'Ue',
        'ä': 'ae',
        'Ä': 'Ae',
        'ß': 'ss'
    }

    def __init__(self):

        self.name = 'Data'

        if path.isfile(DATA_PATH):

            with lock_func:

                log_str('locking {}'.format(self.name))

                try:

                    self.data = load(open(DATA_PATH))
                    self.icon = self.data['currently']['icon']
                    self.temp = self.data['currently']['sensor_temp_outside']
                    self.summary = self.data['currently']['summary']

                    self.hourly_data = self.data['hourly']['data']

                    log_str('init {}'.format(self.__module__))

                except Exception as e:
                    log_str('*** DATA-ERROR: {}'.format(e))

                finally:
                    log_str('releasing {}'.format(self.name))
        else:
            log_str('*** DATA-ERROR: No File')

    def image(self):

        image = ICON_PATH + self.icon + ICON_EXTENSION
        log_str(image)
        return image

    @property
    def temp_str(self):

        self.temp = int(round(self.temp, 0))

        return str(self.temp).zfill(2)

    @property
    def summary_str(self):

        for key in self.replace_me:
            self.summary = self.summary.replace(key, self.replace_me[key])

        return str(self.summary)

    @property
    def time_str(self):

        time_str = strftime(TIMEFORMAT)

        return str(time_str)

    def output_str(self):

        out_str = "{}' {} {} ".format(self.temp_str, self.summary_str, self.time_str)

        return str(out_str)

    def get_rain_forecast(self):

        percentage_list = []
        color = False

        forecast_range_hour = 8

        color_list = []

        for item in self.hourly_data:
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

        log_str('Regenwahrscheinlichkeit 8h: {}'.format(percentage_list[:forecast_range_hour]))
        log_str('Farben auf Display: {}'.format(color_list))

        return color_list


if __name__ == '__main__':
    myData = Data()
    myData.image()
    log_str(myData.summary_str)
    log_str(myData.temp_str)
    log_str(myData.output_str())
    log_str(myData.get_rain_forecast())
