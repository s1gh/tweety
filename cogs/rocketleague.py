import logging
import json
import collections
from math import ceil
from discord.ext import commands
from config import rocketleague_api_key as api_key
from utils.misc import Embed
from datetime import datetime


api_url = 'https://api.rocketleaguestats.com/v1'
top_rank_thumb = "https://rocketleague.tracker.network/Images/RL/ranked/s4-{}.png"
embed_icon = 'http://i.imgur.com/rJDXsLj.png'
tiers = {
    'Unranked': '0',
    'Bronze I': '1',
    'Bronze II': '2',
    'Bronze III': '3',
    'Silver I': '4',
    'Silver II': '5',
    'Silver III': '6',
    'Gold I': '7',
    'Gold II': '8',
    'Gold III': '9',
    'Platinum I': '10',
    'Platinum II': '11',
    'Platinum III': '12',
    'Diamond I': '13',
    'Diamond II': '14',
    'Diamond III': '15',
    'Champion I': '16',
    'Champion II': '17',
    'Champion III': '18',
    'Grand Champion': '19'
}
playlist = {
    '10': 'Solo',
    '11': 'Doubles',
    '12': 'Solo Standard',
    '13': 'Standard'
}
api_status_codes = {
    400: 'Bad Request – Your request seems to be invalid.',
    401: 'Unauthorized – Your API key is wrong.',
    404: 'Not Found – API couldn’t find what you were looking for.',
    405: 'Method Not Allowed – You tried to to access something with an invalid method.',
    406: 'Not Acceptable – You requested a format that isn’t json.',
    429: 'Too Many Requests – You are being rate limited, slow down or request a higher rate limit.',
    500: 'Internal Server Error - API is having problems.',
    503: 'Service Unavailable – API is temporarily offline for maintenance.'
}

log = logging.getLogger(__name__)


class Rocketleague:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rl(self, ctx, uid : str):
        print('test123')
        async with ctx.channel.typing():
            async with self.bot.session.get(api_url + '/player?unique_id={}&platform_id=1&apikey={}'.format(uid, api_key)) as r:
                if r.status != 200:
                    try:
                        log.error(api_status_codes[int(r.status)])
                    except Exception:
                        log.error('Something went wrong when accessing the API (code: {}'.format(r.status))
                elif r.status == 200:
                    data = json.loads(await r.text())

                    em = Embed()
                    em.set_thumbnail(url=top_rank_thumb.format(self.__get_highest_tier(data['rankedSeasons'].get('7'))))  # TODO Get current season programmatically
                    em.set_author(name='Rocket League Rankings For {}'.format(data['displayName']), icon_url=embed_icon)
                    em.set_footer(text='Last Update: {}'.format(
                        datetime.fromtimestamp(data['updatedAt']).strftime('%Y-%m-%d %H:%M:%S')
                    ))

                    for k, v in data['rankedSeasons'].get('7').items():  # TODO Get current season programmatically
                        em.add_field(name=playlist[k], value='**{}**\n----------------\nRating....: {}\nDivision.: {}\nMatches: {}'.format(
                            [key for key, value in tiers.items() if value == str(v['tier'])][0],
                            v['rankPoints'],
                            int(v['division']) + 1,
                            v['matchesPlayed']
                        ))
                    await ctx.send(embed=em)
                else:
                    log.error('Something went wrong when accessing the API (code: {})'.format(r.status))

    @rl.error
    async def rl_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            log.warning('User "{}" is being rate limited.'.format(ctx.message.author))
            await ctx.send('```[INFO] This command is on cooldown, please retry in {} seconds.```'.format(ceil(error.retry_after)))



    def __get_highest_tier(self, tier_data):
        highest_rank = 0
        tier_data = collections.OrderedDict(sorted(tier_data.items()))

        for key, rank in tier_data.items():
            if rank['tier'] > highest_rank:
                highest_rank = rank['tier']
        return highest_rank



def setup(bot):
    bot.add_cog(Rocketleague(bot))