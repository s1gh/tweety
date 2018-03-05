import logging
import sys
from asyncpg import exceptions

log = logging.getLogger(__name__)

class Database:
    def __init__(self, _pool):
        self.pool = _pool

    async def get_db_version(self):
        async with self.pool.acquire() as connection:
            try:
                version = await connection.fetch('SHOW SERVER_VERSION')
            except Exception as err:
                log.error(err)
                return 'N/A'
            else:
                return version[0]['server_version']

    async def execute(self, query, params):
        async with self.pool.acquire() as connection:
            res = await connection.execute(query, *params)
            return res

    async def query(self, query, params):
        async with self.pool.acquire() as connection:
            res = await connection.fetch(query, *params)
            return res

    @classmethod
    async def init_tables(cls, pool):
        async with pool.acquire() as connection:
            try:
                await connection.execute(open('data/tables.sql', 'r').read())
            except exceptions.DuplicateTableError:
                log.info('Database tables already exists. Skipping init_tables()')
            except FileNotFoundError:
                log.critical('Could not find tables.sql. Exiting.')
                sys.exit(-1)
            except Exception as err:
                log.error(err)
                sys.exit(-1)
            else:
                log.info('Successfully created database tables.')