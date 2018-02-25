import subprocess
import logging
import os
import sys
from discord.ext import commands

log = logging.getLogger(__name__)

class Update:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command()
    async def update_test(self, ctx):
        try:
            process = subprocess.Popen(['git', 'pull'], stdout=subprocess.PIPE)
            log.info('Updated to the newest version.')
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as err:
            log.error(err)

def setup(bot):
    bot.add_cog(Update(bot))
