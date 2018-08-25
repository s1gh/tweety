import logging
import re

log = logging.getLogger(__name__)

base_symbol = 'NOK'
currency_api = 'http://api.exchangeratesapi.io/latest?symbols=NOK&base={}'


class Currency:
    def __init__(self, tweety):
        self.bot = tweety

    async def on_message(self, message):
        if message.author.bot:
            return

        q = re.findall('^(\d*\.?\d+)\s([a-zA-Z]+$)', message.content)

        if base_symbol == q[0][1].upper():
            await message.channel.send('```[ERROR] Cannot convert from {} to {}```'.format(base_symbol, base_symbol))
            return

        if q:
            async with self.bot.session.get(currency_api.format(q[0][1].upper())) as r:
                if r.status == 200:
                    try:
                        currency = await r.json()
                        total = float(currency['rates']['NOK']) * float(q[0][0])

                        await message.channel.send('```{} {}```'.format(total, list(currency['rates'].keys())[0]))
                    except KeyError:
                        log.error('Something went wrong with the following request: {}'.format(message.content))


def setup(bot):
    bot.add_cog(Currency(bot))
