#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
from threading import Timer

from requests import get

from modules.Config import *
from modules.Log import lock_func, log_str


class Update(object):

    def __init__(self):

        self.name = 'Update'
        log_str('init {}'.format(self.__module__))

        self.API_ENDPOINT = API_ENDPOINT

    def data_loop(self):

        t = Timer(60, self.data_loop)
        TIMER.append(t)
        t.start()

        try:
            log_str('trying contact url: {}'.format(self.API_ENDPOINT))
            connection = get(self.API_ENDPOINT, timeout=15)
            data = connection.json()

            log_str('status: {} | url: {}'.format(connection.status_code, connection.url))
            log_str('Update done!')

            with lock_func:
                log_str('locking thread {}'.format(t.name))
                try:
                    with open(DATA_PATH, 'w') as outputfile:
                        json.dump(data, outputfile, indent=2, sort_keys=True)
                        log_str('json file saved to {}'.format(DATA_PATH))

                except FileNotFoundError as error:
                    log_str('*** Update-Error: {}'.format(error, DATA_PATH))

                finally:
                    log_str('releasing thread {}'.format(t.name))

        except Exception as exception:

            log_str('*** Update-Exception: {}'.format(exception))


if __name__ == '__main__':

    myUpdate = Update()
    myUpdate.data_loop()
