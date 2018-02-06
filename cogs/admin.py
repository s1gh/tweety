import traceback
import inspect
import discord
from discord.ext import commands
from utils import checks


class Admin:
    def __init__(self, tweety):
        self.bot = tweety

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
