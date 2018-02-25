import json
import logging
import asyncio
import re

log = logging.getLogger(__name__)

currency_api = 'https://api.fixer.io/latest?base=NOK'


class Currency:
    def __init__(self, tweety):
        self.bot = tweety
        self.currencies = {}
        self.currency_update_task = self.bot.loop.create_task(self.currency_updater())

    async def on_message(self, message):
        if message.author.bot:
            return

        q = re.findall('^(\d*\.?\d+)\s([a-zA-Z]+$)', message.content)

        if q and q[0][1].upper() in self.currencies.keys():
            total = float(q[0][0] * float(self.currencies[q[0][1]]))

            await self.bot.send_message(message.channel, '```{}```'.format(total))

    async def currency_updater(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            async with self.bot.session.get(currency_api) as r:
                if r.status == 200:
                    try:
                        currency = json.loads(await r.text())

                        for k,v in currency['rates'].items():
                            self.currencies[k] = v

                        log.info('Downloaded the latest exchange rates with base {}.'.format(currency['base']))
                    except Exception as err:
                        log.error(err)

            await asyncio.sleep(6 * 3600)  # Update every 6 hours


def setup(bot):
    bot.add_cog(Currency(bot))