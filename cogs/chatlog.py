import discord
import time
import logging
import json
from discord.ext import commands
from os import stat
from utils.database import Database
from utils import checks
from asyncpg import exceptions

log = logging.getLogger(__name__)

class ChatLog(Database):
    def __init__(self, tweety):
        super().__init__(tweety.pool)
        self.bot = tweety
        self.excluded_channels = self.load_excluded_channels()

    @checks.is_admin()
    @commands.group(hidden=True)
    async def chatlog(self, ctx):
        pass

    @checks.is_admin()
    @chatlog.command()
    async def exclude(self, ctx, channel: discord.TextChannel):
        try:
            if channel.id not in self.excluded_channels['channels']:
                self.excluded_channels['channels'].append(channel.id)
                self.write_update_to_file()
                await ctx.send('```[INFO] #{} {}```'.format(channel.name, 'is now excluded from the chat log service.'))
            else:
                await ctx.send('```[ERROR] #{} is already excluded from the chat log service.```'.format(channel.name))
        except Exception:
            pass

    @checks.is_admin()
    @chatlog.command()
    async def include(self, ctx, channel: discord.TextChannel):
        try:
            self.excluded_channels['channels'].remove(channel.id)
            self.write_update_to_file()
        except ValueError:
            await ctx.send('```[ERROR] #{} is not an excluded channel.```'.format(channel.name))
        except Exception as err:
            log.error(err)
        else:
            await ctx.send('```[INFO] #{} is now included in the chat log service.```'.format(channel.name))

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id not in self.excluded_channels['channels']:
            params = [
                message.author.id,
                message.content,
                int(time.time()),
                message.guild.id
            ]
            try:
                await self.execute('INSERT INTO chatlog (member_id, message, unix_timestamp, server_id) '
                                   'VALUES ($1, $2, $3, $4)', params)
            except exceptions.UniqueViolationError as err:
                log.error(err)

    @checks.is_admin()
    @chatlog.command()
    async def purge(self, ctx):  # Remove all excluded channels.
        pass

    def load_excluded_channels(self):
        try:
            with open('{}/data/{}'.format(self.bot.base, 'excluded_channels.json'), 'r') as f:
                channels = json.load(f)
        except FileNotFoundError:
            with open('{}/data/{}'.format(self.bot.base, 'excluded_channels.json'), 'w') as f:
                log.info('Could not find excluded_channels.json. Creating a new file.')
                json.dump({'channels': []}, f)
        except json.decoder.JSONDecodeError as err:
            if stat('{}/data/{}'.format(self.bot.base, 'excluded_channels.json')).st_size == 0:
                pass
            else:
                log.error('JSON: {}'.format(err))
        except IOError as err:
            log.error(err)
        else:
            return channels

    def write_update_to_file(self):
        try:
            with open('{}/data/{}'.format(self.bot.base, 'excluded_channels.json'), 'w') as f:
                json.dump(self.excluded_channels, f)
        except IOError as err:
            log.error(err)
        except FileNotFoundError:
            log.error('Could not find excluded_channels.json.')
        except Exception as err:
            log.error(err)

    @exclude.error
    @include.error
    async def chatlog_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('```[ERROR] {}```'.format('That is not a valid text channel.'))


def setup(bot):
    bot.add_cog(ChatLog(bot))