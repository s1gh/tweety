#!/usr/bin/python

import coloredlogs, logging
import contextlib
import argparse
import sys
from tweety import Tweety
from utils.misc import splash_screen

LOG_LEVEL = logging.INFO

@contextlib.contextmanager
def setup_logging(args):
    try:
        # __enter__
        fmt = '%(asctime)s:%(levelname)s:%(name)s->%(funcName)s: %(message)s'
        logging.getLogger('discord').setLevel(LOG_LEVEL)
        log = logging.getLogger()
        log.setLevel(LOG_LEVEL)

        if args.verbose:
            verbose = logging.StreamHandler(sys.stdout)
            verbose.setFormatter(logging.Formatter(fmt))
            log.addHandler(verbose)
            coloredlogs.install(fmt=fmt, logger=logging.getLogger('discord').setLevel(LOG_LEVEL))

        handler = logging.FileHandler(filename='tweety.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter(fmt))
        log.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)

def run_bot():
    bot = Tweety()
    bot.run()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity.')
    args = parser.parse_args()

    with setup_logging(args):
        splash_screen()
        run_bot()


if __name__ == '__main__':
    main()
