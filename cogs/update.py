import subprocess
import logging
import os
import sys
import asyncio
from utils import checks
from discord.ext import commands
from config import update_auto, update_time

log = logging.getLogger(__name__)

class Update:
    def __init__(self, tweety):
        self.bot = tweety
        self.updater = self.bot.loop.create_task(self.updater_service())
        self.auto_update = update_auto

    async def update(self):
        try:
            process = subprocess.Popen(['git', 'pull'], stdout=subprocess.PIPE)
            output = process.communicate()[0]
            up = output.strip().decode('utf-8')
            if up != 'Already up-to-date.':
                log.info('Updated to the latest version.')
                os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as err:
            log.error(err)

    @commands.command(hidden=True, name='update')
    @checks.is_admin()
    async def manual_update(self, ctx):
        await self.update()

    @commands.command(hidden=True, name='autoupdate')
    @checks.is_admin()
    async def activate_auto_update(self, ctx, auto_update: bool = False):
        self.auto_update = auto_update
        log.info('Auto update is now set to {}'.format(auto_update))

    async def updater_service(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            if self.auto_update:
                try:
                    await self.update()
                except Exception as err:
                    log.error(err)
            await asyncio.sleep(update_time * 6)  # Check for updates every 10 minutes  ## DEBUGGING EVERY 60 SEC

    def __unload(self):  # Make sure the background task is destroyed if the cog is unloaded.
        log.warning('Update service is now unloaded and inactive. The bot will NOT automatically update!!')
        self.updater.cancel()


def setup(bot):
    bot.add_cog(Update(bot))
