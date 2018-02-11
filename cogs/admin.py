import traceback
import inspect
import discord
import os
import logging
import sys
from collections import deque
from datetime import datetime
from discord.ext import commands
from utils import checks

log = logging.getLogger(__name__)


class Admin:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command()
    @checks.is_admin()
    async def log(self, ctx, lines: int=5):
        with open('{}/tweety.log'.format(self.bot.base), 'r') as f:
            content = deque(f, lines)
            if len(content) > 0:
                await ctx.send('```python\n{}```'.format(''.join(content)))
            else:
                await ctx.send('```[INFO] Log file is currently empty.```')

    @commands.command()
    async def source(self, ctx, command: str=None):
        """Display the source code of a given command"""
        source_url = 'https://github.com/s1gh/tweety'
        if command is None:
            await ctx.send(source_url)
            return

        obj = self.bot.get_command(command.replace('.', ' '))
        src = obj.callback.__code__
        lines, firstlineno = inspect.getsourcelines(src)

        if not obj.callback.__module__.startswith('discord'):
            # not a built-in command
            location = os.path.relpath(src.co_filename).replace('\\', '/')
        else:
            location = obj.callback.__module__.replace('.', '/') + '.py'
            source_url = 'https://github.com/Rapptz/discord.py'

        final_url = '<{}/blob/master/{}#L{}-L{}>'.format(source_url, location, firstlineno,
                                                         firstlineno + len(lines) - 1)

        if len(lines) < 30:
            lines = [x.replace('```', '´´´') for x in lines]
            await ctx.send('**Source Code: {}**\n```python\n{}\n```'.format(command, ' '.join(lines)))
        else:
            await ctx.send(final_url)

    @commands.command(hidden=True)
    @checks.is_admin()
    async def restart(self, ctx):
        try:
            log.info('Restarted Discord Bot ({}))'.format(ctx.message.author))
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as err:
            log.warning('Failed to restart Discord Bot ({})'.format(err))

    @commands.command(hidden=True)
    @checks.is_admin()
    async def load(self, ctx, *, module : str):
        try:
            self.bot.load_extension('cogs.{}'.format(module))
        except Exception as err:
            await ctx.send('```py\n{}\n```'.format(traceback.format_exc()))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @checks.is_admin()
    async def unload(self, ctx, *, module : str):
        try:
            self.bot.unload_extension('cogs.{}'.format(module))
        except Exception as err:
            await ctx.send('```py\n{}\n```'.format(traceback.format_exc()))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @checks.is_admin()
    async def _reload(self, ctx, *, module : str):
        try:
            self.bot.unload_extension('cogs.{}'.format(module))
            self.bot.load_extension('cogs.{}'.format(module))
        except Exception as err:
            await ctx.send('```py\n{}\n```'.format(traceback.format_exc()))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @checks.is_admin()
    async def debug(self, ctx, *, code : str):
        """Evaluates code."""
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'tweety': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.message.server,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(python.format(type(e).__name__ + ': ' + str(e)))
            return
        await ctx.send(python.format(result))

    @commands.command(hidden=True)
    @checks.is_admin()
    async def status(self, ctx, *, game : str=None):
        if game is None:
            await self.bot.change_presence(game=discord.Game())
        else:
            await self.bot.change_presence(game=discord.Game(name=game))

    @commands.command(hidden=True)
    @checks.is_admin()
    async def avatar(self, ctx, *, filename : str=None):
        try:
            with open('avatars/{}'.format(filename), 'rb') as f:
                await self.bot.user.edit(avatar=f.read())
        except IOError:
            await ctx.send('```py\n{}\n```'.format(traceback.format_exc()))



def setup(bot):
    bot.add_cog(Admin(bot))
