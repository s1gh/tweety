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
            output = process.communicate()[0]
            up = output.strip().decode('utf-8')
            if up != 'Already up-to-date.':
                log.info('Updated to the newest version.')
                os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as err:
            log.error(err)
            
    @commands.command()
    async def testing(self, ctx):
        await ctx.send('Update feature is working. This function was pulled from Github. Jey')

def setup(bot):
    bot.add_cog(Update(bot))
