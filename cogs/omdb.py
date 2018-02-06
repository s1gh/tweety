import json
import logging
import config
import re
from discord.ext import commands

log = logging.getLogger(__name__)

class Omdb:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command()
    async def omdb(self, ctx, *, title : str):
        release_date = re.findall(r'\[([0-9]+)\]', title)

        async with self.bot.session.get(config.omdb_api_url.format(title, '', config.omdb_api_key)) as resp:
            log.info('OMDB API returned status: {}'.format(resp.status))
            if resp.status == 200:
                data = json.loads(await resp.text())
                print(data)



def setup(bot):
    bot.add_cog(Omdb(bot))