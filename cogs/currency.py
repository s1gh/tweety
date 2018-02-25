import json
import logging
import asyncio

log = logging.getLogger(__name__)

currency_api = 'https://api.fixer.io/latest'


class Currency:
    def __init__(self, tweety):
        self.bot = tweety
        self.currencies = {}
        self.currency_update_task = self.bot.loop.create_task(self.currency_updater())

    async def currency_updater(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            async with self.bot.session.get(currency_api) as r:
                currency = json.loads(await r.text())

                for k,v in currency['rates'].items():
                    self.currencies[k] = v

            asyncio.sleep(6 * 3600)  # Update every 6 hours


    async def on_message(self, message):
        pass