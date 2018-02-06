import discord
import sys
import os
from pymongo import version as pymongo_version
from discord.ext import commands
from utils.misc import Embed, LinesOfCode, Uptime, Birthday

BOT_INFO_THUMBNAIL = 'https://s22.postimg.org/bgtc198pt/tweety_angry.png'
PYTHON_ICON = 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/' \
              'Python-logo-notext.svg/2000px-Python-logo-notext.svg.png'

class Info:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.group()
    async def info(self, ctx):
        if ctx.invoked_subcommand is None:
            em = Embed()
            em.set_thumbnail(url=BOT_INFO_THUMBNAIL)
            em.set_author(name='Tweety', url='https://github.com/s1gh/Tweety_2.0')
            em.add_field(name="Library", value='Discord.py ({})'.format(discord.__version__))
            em.add_field(name="Database", value='MongoDB ({})'.format(pymongo_version))
            em.add_field(name="Lines of Code", value=LinesOfCode().loc(root=self.bot.base))
            em.add_field(name="Loaded Plugins", value=str(len(self.bot.extensions)))
            em.add_field(name="Developer", value="s1gh#9750")
            em.add_field(name="Birthday", value=Birthday(self.bot.user.created_at).get_birthday())
            em.set_footer(text='Created with Python {} | Uptime: {}'.format(sys.version[:6], Uptime(self.bot.uptime).uptime()), icon_url=PYTHON_ICON)

            await ctx.send(embed=em)

    @info.command()
    async def uptime(self, ctx):
        await ctx.send('```python\n{}```'.format(Uptime(self.bot.uptime).uptime()))


    @info.command()
    async def profile(self, ctx, *, user : discord.Member):
        print('testing')


def setup(bot):
    bot.add_cog(Info(bot))
