import logging
import json
import collections
import re
from math import ceil
from discord.ext import commands
from config import rocketleague_api_key as api_key
from utils.misc import Embed
from datetime import datetime
from bs4 import BeautifulSoup


api_url = 'https://rocketleague.tracker.network/profile/steam/{}'
top_rank_thumb = "https://rocketleague.tracker.network/Images/RL/ranked/s4-{}.png"
embed_icon = 'http://i.imgur.com/rJDXsLj.png'
tiers = {
    'Unranked': 0,
    'Bronze I': 1,
    'Bronze II': 2,
    'Bronze III': 3,
    'Silver I': 4,
    'Silver II': 5,
    'Silver III': 6,
    'Gold I': 7,
    'Gold II': 8,
    'Gold III': 9,
    'Platinum I': 10,
    'Platinum II': 11,
    'Platinum III': 12,
    'Diamond I': 13,
    'Diamond II': 14,
    'Diamond III': 15,
    'Champion I': 16,
    'Champion II': 17,
    'Champion III': 18,
    'Grand Champion': 19
}

renamed_playlists = {
    'Ranked Duel 1v1': 'Solo',
    'Ranked Doubles 2v2': 'Doubles',
    'Ranked Solo Standard 3v3': 'Solo Standard',
    'Ranked Standard 3v3': 'Standard'
}


division = {
    'Division I': 'I',
    'Division II': 'II',
    'Division III': 'III',
    'Division IV': 'IV'
}

log = logging.getLogger(__name__)

PLAYLIST = [
    'Solo',
    'Doubles',
    'Solo Standard',
    'Standard'
]


class Rocketleague:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)  # 5 second cooldown per user
    async def rl(self, ctx, uid : str):
        """Fetch competetive statistics for a given user"""
        async with self.bot.session.get(api_url.format(uid)) as r:
            if r.status != 200:
                log.error('Got error code "{}"'.format(r.status))
            else:
                try:
                    soup = BeautifulSoup(await r.text(), features="html.parser")
                    try:
                        rank_data = soup.find('div', {'id': 'season-11'}).findAll('table', {'class': 'card-table items'})[1].find('tbody').findAll('tr')
                        reward_level = \
                        soup.find('div', {'id': 'season-11'}).find('table', {'class': 'card-table items'}).find('tbody').findAll(
                        'td')[1].text.strip().split('\n\n')[1]
                    except IndexError:
                        rank_data = soup.find('div', {'id': 'season-11'}).findAll('table', {'class': 'card-table items'})[
                            0].find('tbody').findAll('tr')
                        reward_level = 'Unranked'

                    em = Embed()
                    em.set_author(name='RL Overview - {}'.format(uid), icon_url=embed_icon)

                    em.add_field(name="Main Competitive Playlists", value="------------------------------------------------------", inline=False)
                    for rank in rank_data:
                        rank_title = rank.findAll('td')[1].text.split('\n\n')[0].strip()
                        rank_mmr = rank.findAll('td')[3].text.strip().split('\n')[0].replace(',', '')
                        rank_division = rank.findAll('td')[1].text.split('\n\n')[1].split('\n')[1].strip()
                        games_played = rank.findAll('td')[5].text.strip().split('\n')[0].strip()

                        if rank_title != 'Un-Ranked':
                            rank_title = rank_title if rank_title not in renamed_playlists else renamed_playlists[
                                rank_title]
                            rank_num = self.get_rank_from_img(rank.find('img')['src'])
                            rank = list(tiers.keys())[list(tiers.values()).index(rank_num)]

                            em.add_field(name=rank_title,
                                         value='**{}**\n----------------\nRating....: {}\nDivision.: {}\nMatches: {}'.
                                         format(rank, rank_mmr, division[rank_division], games_played))

                            if rank_title == "Standard":
                                em.add_field(name="Other Playlists", value="------------------------------------------------------", inline=False)
                        else:
                            em.set_footer(text='Unranked MMR: {} | Reward Level: {}'.format(rank_mmr, reward_level))

                    em.set_thumbnail(url='https://rocketleague.tracker.network/Images/RL/ranked/s4-{}.png'.format(
                        self.__get_highest_tier(rank_data) or 0))

                    await ctx.send(embed=em)
                except Exception as err:
                    log.error(err)
                    await ctx.send('```[ERROR] Could not find player {}```'.format(uid))


    @rl.error
    async def rl_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            log.warning('User "{}" is being rate limited.'.format(ctx.message.author))
            await ctx.send('```[INFO] This command is on cooldown, please retry in {} seconds.```'.format(ceil(error.retry_after)))

    def __get_highest_tier(self, rank_data):
        ranks = []

        for rank in rank_data:
            ranks.append(int(self.get_rank_from_img(rank.find('img')['src'])))

        return max(ranks)

    def get_rank_from_img(self, img_src):
        return int(re.findall('s4-([0-9]+)', img_src)[0])


def setup(bot):
    bot.add_cog(Rocketleague(bot))
