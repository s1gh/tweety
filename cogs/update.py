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
            process = subprocess.Popen(['git', 'pull', '--ff-only'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdoutput, stderroutput = process.communicate()

            if process.returncode == 0 and 'Already up-to-date.' not in stdoutput.decode('utf-8').strip():
                log.info('Updated to the latest version.')
                os.execv(sys.executable, ['python'] + sys.argv)
            elif process.returncode != 0:
                log.critical('Update process failed. Your install seem to be broken. '
                      'You can try to repair the bot using the --repair argument at startup.')
        except Exception as err:
            log.error(err)

    @commands.command(hidden=True, name='update')
    @checks.is_admin()
    async def manual_update(self, ctx):
        await self.update()

    @commands.command(hidden=True, name='autoupdate')
    @checks.is_admin()
    async def set_auto_update(self, ctx, up: bool = False):
        self.auto_update = up
        log.warning('Auto update is now set to {}'.format(up))

        await ctx.send('```[INFO] Auto update is now set to {}```'.format(up))

    async def updater_service(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            if self.auto_update:
                try:
                    log.info('Checking repository for new updates.')
                    await self.update()
                except Exception as err:
                    log.error(err)
            await asyncio.sleep(update_time * 60)  # Check for updates every hour

    def __unload(self):  # Make sure the background task is destroyed if the cog is unloaded.
        log.warning('Update service is now unloaded and inactive. The bot will NOT automatically update!!')
        self.updater.cancel()


def setup(bot):
    bot.add_cog(Update(bot))
