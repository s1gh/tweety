import json
import logging
import asyncio
import re
from utils.misc import Embed

crypto_api = 'https://min-api.cryptocompare.com/data/{}'
embed_thumb = 'https://cdn2.iconfinder.com/data/icons/bitcoin-and-mining/44/trade-512.png'
convert_to = 'EUR'

log = logging.getLogger(__name__)


class Currency:
    def __init__(self, tweety):
        self.bot = tweety
        self.coin_data = {}
        self.coins_download_task = self.bot.loop.create_task(self.coins_background_task())

    async def on_message(self, message):
        if message.author.bot:
            return

        q = re.findall('^(\d*\.?\d+)\s([a-zA-Z]+$)', message.content)

        if q:
            async with self.bot.session.get(crypto_api.format('pricemultifull?fsyms=' + q[0][1].upper() + '&tsyms=EUR')) as r:
                if r.status == 200:
                    data = json.loads(await r.text())

                    if data['RAW']:
                        em = Embed(url='https://www.cryptocompare.com{}'.format(self.coin_data[q[0][1].upper()]['URL']),
                                   title='{} ({})'.format(
                                       self.coin_data[q[0][1].upper()]['Name'],
                                       q[0][1].upper()
                                   ))
                        em.set_author(name='Crypto Currency', icon_url=embed_thumb)
                        try:
                            em.set_thumbnail(url='https://www.cryptocompare.com{}'.format(
                                self.coin_data[q[0][1].upper()]['Image']
                            ))
                        except KeyError as err:
                            em.set_thumbnail(url='http://simpleicon.com/wp-content/uploads/coin-money-4.png')

                        em.add_field(name='Exchange Rate', value='{} {}'.format(
                            data['RAW'][q[0][1].upper()][convert_to]['PRICE'],
                            convert_to
                        ))
                        em.add_field(name='Algorithm', value=self.coin_data[q[0][1].upper()]['Algo'])
                        em.add_field(name='Premined', value=self.coin_data[q[0][1].upper()]['Premined'] if not '0' else 'No')
                        em.add_field(name='Total Supply', value=self.coin_data[q[0][1].upper()]['Supply'])
                        em.add_field(name='Change Last 24h', value=data['RAW'][q[0][1].upper()][convert_to]['CHANGE24HOUR'])

                        await message.channel.send(embed=em)

    def __unload(self):  # Make sure the background task is destroyed if the extension is unloaded.
        self.coins_download_task.cancel()

    async def coins_background_task(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            async with self.bot.session.get(crypto_api.format('all/coinlist')) as r:
                if r.status == 200:
                    data = json.loads(await r.text())
                    for coin in data['Data'].items():
                        try:
                            self.coin_data[coin[1]['Name']] = {
                                'Name': coin[1]['CoinName'],
                                'Algo': coin[1]['Algorithm'],
                                'Premined': int(coin[1]['FullyPremined']),
                                'Supply': coin[1]['TotalCoinSupply'],
                                'Image': coin[1]['ImageUrl'],
                                'URL': coin[1]['Url']
                            }
                        except KeyError:
                            pass
                    log.info('Downloaded information about {} coins from CryptoCompare.'.format(len(self.coin_data)))
                else:
                    log.error('There was a problem downloading coinlist from CryptoCompare (error {})'.format(r.status))
            await asyncio.sleep(43200)  # Run this task every 12 hours (3600 seconds * 12 hours)


def setup(bot):
    bot.add_cog(Currency(bot))
