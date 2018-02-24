import traceback
import inspect
import discord
import os
import logging
import sys
import subprocess
import imghdr
from collections import deque
from discord.ext import commands
from utils import checks

log = logging.getLogger(__name__)

allowed_image_types = [
    'jpeg',
    'png'
]


class Admin:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command(hidden=True, name='exec')
    @checks.is_admin()
    async def execute(self, ctx, *, command: str):
        try:
            out = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).communicate()[0].strip().decode('utf-8')
            await ctx.send('```python\n{}```'.format(out))
        except Exception as err:
            print(err)
            return

    @commands.command(hidden=True)
    @checks.is_admin()
    async def nick(self, ctx, member: discord.Member, *, nickname: str=None):
        try:
            await member.edit(nick=nickname)
        except discord.Forbidden:
            log.critical('Bot does not have the proper permissions to change nicknames.')

    @commands.command(hidden=True)
    @checks.is_admin()
    async def log(self, ctx, lines: int=5):
        with open('{}/tweety.log'.format(self.bot.base), 'r') as f:
            content = deque(f, lines)
            if len(content) > 0:
                await ctx.send('```python\n{}```'.format(''.join(content)))
            else:
                await ctx.send('```[INFO] Log file is currently empty.```')

    @commands.command(hidden=True)
    @checks.is_admin()
    async def restart(self, ctx):
        try:
            await ctx.send('```[INFO] Restarting...```')
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

    @commands.command(hidden=True)  # InvalidArgument – Wrong image format passed for avatar.
    @checks.is_admin()
    async def avatar(self, ctx, *, filename : str=None):
        if filename is None:
            try:
                with open('avatars/tweety_angry.png', 'rb') as f:
                    await self.bot.user.edit(avatar=f.read())
                    log.info('Restored avatar back to the default value.')
            except IOError:
                await ctx.send('```py\n{}\n```'.format(traceback.format_exc()))
            except discord.errors.HTTPException as err:
                log.error(err)

        elif filename.startswith('http'):
            try:
                async with self.bot.session.get(filename) as in_file:
                    img = await in_file.read()
                    if imghdr.what(file=' ', h=img) in allowed_image_types:
                        await self.bot.user.edit(avatar=img)
                        log.info('Downloaded image and updated profile to reflect avatar change.')
            except discord.errors.HTTPException as err:
                log.error(err)


def setup(bot):
    bot.add_cog(Admin(bot))
