import discord
import sys
import os
import inspect
from pymongo import version as pymongo_version
from discord.ext import commands
from utils.misc import Embed, LinesOfCode, Uptime, Birthday

bot_info_thumb = 'https://s22.postimg.org/bgtc198pt/tweety_angry.png'
python_icon = 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/' \
              'Python-logo-notext.svg/2000px-Python-logo-notext.svg.png'
embed_profile_icon = 'https://www.iconsdb.com/icons/preview/black/manager-xxl.png'
embed_gaming_icon = 'https://cdn.iconscout.com/public/images/icon/free/png-512/' \
                    'videogame-mushroom-toad-mario-bros-3cf1084383a9c2e6-512x512.png'

class Info:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.group()
    async def info(self, ctx):
        if ctx.invoked_subcommand is None:
            em = Embed()
            em.set_thumbnail(url=bot_info_thumb)
            em.set_author(name='Tweety', url='https://github.com/s1gh/tweety/')
            em.add_field(name="Library", value='Discord.py ({})'.format(discord.__version__))
            em.add_field(name="Database", value='MongoDB ({})'.format(pymongo_version))
            em.add_field(name="Lines of Code", value=LinesOfCode().loc(root=self.bot.base))
            em.add_field(name="Loaded Plugins", value=str(len(self.bot.extensions)))
            em.add_field(name="Developer", value="s1gh#9750")
            em.add_field(name="Birthday", value=Birthday(self.bot.user.created_at).get_birthday())
            em.set_footer(text='Created with Python {} | Uptime: {}'.format(sys.version[:6], Uptime(self.bot.uptime).uptime()), icon_url=python_icon)

            await ctx.send(embed=em)

    @info.command()
    async def uptime(self, ctx):
        """Get the current uptime"""

        await ctx.send('```python\n{}```'.format(Uptime(self.bot.uptime).uptime()))

    @info.command()
    async def source(self, ctx, command: str=None):
        """Display the source code for a specific command"""

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

    @info.command()
    async def server(self, ctx):
        """Fetch information about the server"""

        em = Embed()
        em.set_author(name=ctx.guild.name)
        em.set_thumbnail(url=ctx.guild.icon_url)
        em.add_field(name='Created', value=ctx.guild.created_at.strftime('%d/%m/%Y %H:%M:%S'))
        em.add_field(name='Region', value=ctx.guild.region.name.upper())
        em.add_field(name='Members', value=ctx.guild.member_count)
        em.add_field(name='Owner', value=ctx.guild.owner)
        em.add_field(name='Roles', value=', '.join(role.name for role in ctx.guild.roles), inline=False)

        await ctx.send(embed=em)

    @info.command(aliases=['about'])
    async def profile(self, ctx, *, user : discord.Member):
        """Fetch information about a user"""

        em = Embed()
        em.set_thumbnail(url=user.avatar_url)
        em.set_author(name='Profile Information')
        em.add_field(name='Display Name', value=user.display_name)
        em.add_field(name='Discriminator', value=user.discriminator)
        em.add_field(name='Created', value=user.created_at.strftime('%d/%m/%Y %H:%M:%S'))
        em.add_field(name='Joined', value=user.joined_at.strftime('%d/%m/%Y %H:%M:%S'))
        em.add_field(name='Account Type', value='User' if not user.bot else 'Bot')
        em.add_field(name='Roles', value=', '.join(x.name for x in user.roles), inline=False)
        em.set_footer(text='Currently playing: {}'.format(user.game or 'Nothing'))

        await ctx.send(embed=em)

    @profile.error
    async def profile_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('```[ERROR] {}.```'.format(error))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('```[ERROR] {}```'.format(error))

def setup(bot):
    bot.add_cog(Info(bot))
