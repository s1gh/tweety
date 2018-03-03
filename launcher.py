#!/usr/bin/python

import coloredlogs, logging
import contextlib
import argparse
import sys
import asyncio
import aioodbc
from tweety import Tweety
from utils.misc import splash_screen, git_repair
from config import db_name, db_pool_size

LOG_LEVEL = logging.INFO

@contextlib.contextmanager
def setup_logging(args):
    try:
        # __enter__
        fmt = '%(asctime)s:%(levelname)s:%(name)s->%(funcName)s: %(message)s'
        logging.getLogger('discord').setLevel(LOG_LEVEL)
        log = logging.getLogger()
        log.setLevel(LOG_LEVEL)

        handler = logging.FileHandler(filename='tweety.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter(fmt))
        log.addHandler(handler)

        if args.verbose:
            verbose = logging.StreamHandler(sys.stdout)
            verbose.setFormatter(logging.Formatter(fmt))
            log.addHandler(verbose)
            coloredlogs.install(fmt=fmt, logger=logging.getLogger('discord').setLevel(LOG_LEVEL))
        if args.repair:
            git_repair()

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)

def run_bot():
    loop = asyncio.get_event_loop()
    log = logging.getLogger()

    try:
        pool = loop.run_until_complete(create_db_pool(loop))
    except Exception:
        log.critical('Could not setup database. Exiting.')
        return

    bot = Tweety()
    bot.pool = pool
    bot.run()

async def create_db_pool(loop):
    dsn = 'Driver=SQLite3;Database=data/{}'.format(db_name)
    pool = await aioodbc.create_pool(dsn=dsn, loop=loop, minsize=db_pool_size, maxsize=db_pool_size)

    return pool


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Show every message being logged by the bot.')
    parser.add_argument('-r', '--repair', action='store_true', help='Attempts to repair a broken version of the bot.')
    args = parser.parse_args()

    with setup_logging(args):
        splash_screen()
        run_bot()


if __name__ == '__main__':
    main()
