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

    @commands.group(hidden=True)
    async def cc(self, ctx):
        pass

    @checks.is_admin()
    @cc.command(aliases=['create'])
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
            if ctx.guild.id in self.cc_map.keys():
                self.cc_map[ctx.guild.id][trigger_word] = trigger_text
            else:
                self.cc_map[ctx.guild.id] = {trigger_word: trigger_text}
            await ctx.send('```[INFO] {}```'.format('Custom command successfully created.'))

    @checks.is_admin()
    @cc.command(aliases=['change', 'update'])
    async def edit(self, ctx, trigger_word: str, trigger_text: str):
        try:
            ret = await self.execute('UPDATE custom_command '
                                     'SET trigger_text = $1 '
                                     'WHERE trigger_word = $2 AND server_id = $3', [trigger_text,
                                                                                    trigger_word,
                                                                                    ctx.guild.id])
        except Exception as err:
            log.error(err)
        else:
            if int(ret[-1:]):
                self.cc_map[ctx.guild.id][trigger_word] = trigger_text
                await ctx.send('```[INFO] Custom command "{}" updated successfully.```'.format(trigger_word))
            else:
                await ctx.send('```[ERROR] Could not update custom command "{}". '
                               'Are you sure it exist on this guild?```'.format(trigger_word))

    @checks.is_admin()
    @cc.command(aliases=['remove', 'purge'])
    async def delete(self, ctx, trigger_word: str):
        try:
            ret = await self.execute('DELETE FROM custom_command '
                                   'WHERE server_id = $1 '
                                   'AND trigger_word = $2', [ctx.guild.id, trigger_word])
        except Exception as err:
            log.error(err)
        else:
            if int(ret[-1:]):
                del self.cc_map[ctx.guild.id][trigger_word]
                await ctx.send('```[INFO] Custom command "{}" removed from database successfully.```'.format(trigger_word))
            else:
                await ctx.send('```[ERROR] Could not delete custom command "{}". Are you sure it exist?```'.format(trigger_word))

    @cc.command(name='list')
    async def _list(self, ctx):  # Use internal cc_map instead.
        try:
            res = await self.query('SELECT trigger_word '
                                   'FROM custom_command '
                                   'WHERE server_id = $1', [ctx.guild.id])
        except Exception as err:
            log.error(err)
        else:
            if len(res) > 0:
                await ctx.send('**Custom Commands**\n```{}```'.format(', '.join([x['trigger_word'] for x in res])))
            else:
                await ctx.send('```[INFO] Could not find any custom commands for this guild.```')


    async def populate_commands(self):
        try:
            commands = await self.query('SELECT trigger_word, trigger_text, server_id '
                                        'FROM custom_command', [])
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
