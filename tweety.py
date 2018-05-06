try:
    import config
except ImportError:
    print('Error: Could not start the bot. Please make sure the config file exist in the root directory.')
    raise SystemExit
import aiohttp
import traceback
import datetime
import os
from discord.ext import commands
from pathlib import Path

plugins = [
    'cogs.admin',
    'cogs.rocketleague',
    'cogs.info',
    'cogs.troll',
    'cogs.cryptocurrency',
    'cogs.currency',
    'cogs.update',
    'cogs.tvmaze',
    'cogs.alias',
    'cogs.customcommand',
    'cogs.tags',
    'cogs.chatlog',
    'cogs.stats',
    'cogs.omdb',
    'cogs.quotes',
    'cogs.markov',
    'cogs.reminders'
]

class Tweety(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(*['?', '+']), description='', pm_help=None)
        self.client_id = config.discord_client_id
        self.session = aiohttp.ClientSession(loop=self.loop)

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            if Path('uptime.up').is_file():  # Check if the bot has restarted because of an update (keep uptime)
                with open('uptime.up', 'r') as f:
                    self.uptime = datetime.datetime.strptime(f.readline(), '%Y-%m-%d %H:%M:%S.%f')
                os.remove('uptime.up')
            else:
                self.uptime = datetime.datetime.utcnow()
        if not hasattr(self, 'base'):
            self.base = os.path.dirname(os.path.abspath(__file__))

        for plugin in plugins:
            try:
                self.load_extension(plugin)
            except Exception as err:
                print('Failed to load plugin {}'.format(plugin))
                traceback.print_exc()

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    def run(self):
        super().run(config.discord_token, reconnect=True)
