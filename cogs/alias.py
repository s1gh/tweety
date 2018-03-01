import json
import logging
from copy import copy
from discord.ext import commands

log = logging.getLogger(__name__)

class Alias:
    def __init__(self, tweety):
        self.bot = tweety
        try:
            with open('{}/{}'.format(self.bot.base, 'alias_map.json'), 'r') as f:
                self.alias_map = json.load(f.read())
        except IOError:
            with open('{}/{}'.format(self.bot.base, 'alias_map.json'), 'w'):
                self.alias_map = {}
            log.warning('Could not open alias_map.json. Created new file...')

    async def on_message(self, message):
        if message.author.id in self.alias_map:

            print(self.bot.base)

            prefix = await self.bot.get_prefix(message)

            cmd = self.alias_map[message.author.id][message.content]
            msg = copy(message)

            msg.content = '{}{}'.format(prefix[0], cmd)

            await self.bot.process_commands(msg)


def setup(bot):
    bot.add_cog(Alias(bot))