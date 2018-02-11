#!/usr/bin/python

import asyncio
import logging
import datetime
import contextlib
from tweety import Tweety

@contextlib.contextmanager
def setup_logging():
    try:
        # __enter__
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord').setLevel(logging.WARNING)

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = logging.FileHandler(
            filename='tweety-{}.log'.format(datetime.datetime.now().strftime('%d-%m-%Y')), encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        log.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)

def run_bot():
    #loop = asyncio.get_event_loop()
    #log = logging.getLogger()
    bot = Tweety()
    bot.run()

def main():
    #loop = asyncio.get_event_loop()
    with setup_logging():
        run_bot()


if __name__ == '__main__':
    main()