import logging
import asyncio
from datetime import datetime
from discord.ext import commands
from utils.database import Database
from asyncpg import exceptions
from utils import checks

log = logging.getLogger(__name__)
loop = asyncio.get_event_loop()

class CustomCommand(Database):
    def __init__(self, tweety):
        self.bot = tweety
        self.cc_map = {}
        super().__init__(self.bot.pool)
        loop.create_task(self.populate_commands())

    @commands.group()
    async def cc(self, ctx):
        pass

    @checks.is_admin()
    @cc.command()
    async def add(self, ctx, trigger_word: str, trigger_text: str):
        params = [
            ctx.message.author.id,
            trigger_word.lower(),
            trigger_text,
            datetime.now(),
            ctx.message.guild.id,
        ]

        try:
            await self.execute('INSERT INTO custom_command (member_id, trigger_word, trigger_text, timestamp, server_id) '
                               'VALUES ($1, $2, $3, $4, $5)', params)
        except exceptions.UniqueViolationError:
            await ctx.send('```[ERROR] {}```'.format('A custom command with that name already exist.'))
        except Exception as err:
            log.error(err)
        else:
            await ctx.send('```[INFO] {}```'.format('Custom command successfully created.'))


    async def populate_commands(self):
        try:
            commands = await self.query('SELECT trigger_word, trigger_text, server_id FROM custom_command', [])
        except Exception as err:
            log.error(err)
        else:
            for cmd in commands:
                if cmd['server_id'] in self.cc_map:
                    self.cc_map[cmd['server_id']].update({
                            cmd['trigger_word']: cmd['trigger_text']
                    })
                else:
                    self.cc_map[cmd['server_id']] = {
                        cmd['trigger_word']: cmd['trigger_text']
                    }

    async def on_message(self, message):
        if message.author.bot:
            return
        try:
            reply = self.cc_map[message.guild.id][message.content]
        except KeyError:
            pass
        except Exception as err:
            log.error(err)
        else:
            await message.channel.send(reply)


def setup(bot):
    bot.add_cog(CustomCommand(bot))
