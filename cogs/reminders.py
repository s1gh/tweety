import datetime
import asyncio
import logging
import discord
from utils.database import Database
from discord.ext import commands

log = logging.getLogger(__name__)

class Reminder():
    def __init__(self, member, created, server_id, reminder, timestamp):
        self._member = member
        self._created_at = created
        self._guild = server_id
        self._reminder = reminder
        self._timestamp = timestamp

    def __gt__(self, other):
        if isinstance(other, datetime.datetime):
            return self._timestamp > other
        return NotImplemented

    @property
    def member(self):
        return self._member

    @property
    def guild(self):
        return self._guild

    @property
    def reminder(self):
        return self._reminder

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def created(self):
        return self._created_at


class Reminders(Database):
    def __init__(self, tweety):
        self.bot = tweety
        self.reminder_list = []
        super().__init__(self.bot.pool)
        self.reminders_task = self.bot.loop.create_task(self.check_reminders())

    @commands.command(aliases=['reminder'])
    async def remindme(self, ctx, time: int, unit: str, *, reminder: str):
        """A way for members to create their own reminders.
        Valid units: seconds, minutes, hours, days, weeks
        Example: remindme 15 minutes Take the pizza out of the oven."""
        try:
            if time < 0:
                await ctx.send('```[ERROR] Time cannot be a negative value.```')
                return

            now = datetime.datetime.now()
            params = [
                ctx.author.id,
                now,
                ctx.guild.id,
                reminder,
                (now + datetime.timedelta(**{unit: time})).replace(microsecond=0)
            ]

            await self.execute('INSERT INTO reminders (member, created, server_id, reminder, timestamp) '
                                'VALUES ($1, $2, $3, $4, $5)', params)
        except TypeError as err:
            log.error(err)
        else:
            await ctx.send('Alright {}, I\'ll send you a PM in {} {}.'.format(ctx.message.author.mention,
                                                                              time,
                                                                              unit[:-1] if time == 1 else unit))
            self.reminder_list.append(Reminder(params[0], params[1], params[2], params[3], params[4]))

    async def fetch_from_db(self):
        res = await self.query('SELECT member, created, server_id, reminder, timestamp '
                               'FROM reminders '
                               'WHERE timestamp::timestamp > current_timestamp', [])

        return [Reminder(x['member'], x['created'], x['server_id'], x['reminder'], x['timestamp']) for x in res]

    async def check_reminders(self):
        await self.bot.wait_until_ready()
        self.reminder_list = await self.fetch_from_db()

        while not self.bot.is_closed():
            if len(self.reminder_list) > 0:
                for obj in list(self.reminder_list):  # Iterate over copy and remove from the original :'(
                    if obj.timestamp <= datetime.datetime.now():
                        try:
                            member = discord.utils.get(self.bot.get_all_members(), id=obj.member)
                            reminder = 'Hi there! :heart_eyes: \n\nAt {} you asked me to remind you of the following' \
                                       ':\n"{}"'.format(obj.created.strftime('%d.%m.%y %H:%M:%S'), obj.reminder)

                            await member.send(reminder)

                            self.reminder_list.remove(obj)
                        except Exception as err:
                            log.error(err)
            await asyncio.sleep(1)

    @remindme.error
    async def remindme_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('```[ERROR] Bad argument.```'.format(error))

    def __unload(self):  # Make sure the background task is destroyed if the cog is unloaded.
        self.reminders_task.cancel()
        del self.reminder_list[:]
        log.warning('Reminder task is now unloaded.')

def setup(bot):
    bot.add_cog(Reminders(bot))
