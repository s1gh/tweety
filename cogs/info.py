"""
This module allows users to get information about members, the server, last update on Github etc.
"""

import discord
import sys
import os
import inspect
import subprocess
from config import github_access_token, github_repo_name
from github import Github
from pymongo import version as pymongo_version
from discord.ext import commands
from utils.misc import Embed, LinesOfCode, Uptime, Birthday
from utils.database import Database

bot_info_thumb = 'https://s22.postimg.org/bgtc198pt/tweety_angry.png'
python_icon = 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/' \
              'Python-logo-notext.svg/2000px-Python-logo-notext.svg.png'
plugin_embed_thumb = 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97' \
                     '/Circle-icons-plugin.svg/2000px-Circle-icons-plugin.svg.png'

class Info(Database):
    def __init__(self, tweety):
        self.bot = tweety
        self.github = Github(github_access_token).get_user().get_repo(github_repo_name)
        super().__init__(self.bot.pool)


    @commands.group()
    async def info(self, ctx):
        """Get info about the bot or other users"""
        if ctx.invoked_subcommand is None:
            async with ctx.typing():
                last_git_sha_hash = self.github.get_commits(sha='master')[0].sha
                process = subprocess.Popen(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                local_hash = process.communicate()[0].decode('utf-8').strip()

                update_status = '{}'.format('Running the latest version of Tweety.' if last_git_sha_hash == local_hash
                                            else 'New update available.')

                em = Embed()
                em.set_thumbnail(url=bot_info_thumb)
                em.set_author(name='Tweety', url='https://github.com/s1gh/tweety/')
                em.add_field(name="Library", value='Discord.py ({})'.format(discord.__version__))
                em.add_field(name="Database", value='PostgreSQL {}'.format(await self.get_db_version()))
                em.add_field(name="Lines of Code", value=LinesOfCode().loc(root=self.bot.base))
                em.add_field(name="Plugins", value=str(len(self.bot.extensions)))
                em.add_field(name="Developer", value="s1gh#9750")
                em.add_field(name="Birthday", value=Birthday(self.bot.user.created_at).get_birthday())
                em.set_footer(text='Created with Python {} | Status: {}'.format(sys.version[:6], update_status),
                              icon_url=python_icon)

                await ctx.send(embed=em)

    @info.command(name='plugins')
    async def list_plugins(self, ctx):
        em = Embed()
        em.set_thumbnail(url=plugin_embed_thumb)
        em.set_author(name='Plugins')

        for k, v in self.bot.extensions.items():
            em.add_field(name=k[5:].capitalize(), value=v.__doc__ or 'No docstring found.', inline=False)

        await ctx.send(embed=em)

    @info.command(name='commit')
    async def last_commit(self, ctx):
        """Get the latest commit to Github"""

        commit = self.github.get_commits(sha='master')[0]

        await ctx.send('```[{}] {}: {}```'.format(commit.commit.last_modified, commit.sha[:7], commit.commit.message))

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
        """Get information about the server"""
        print(dir(ctx.guild))
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
        """Get information about a user"""

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
