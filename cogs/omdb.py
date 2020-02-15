import logging
import re
from discord.ext import commands
from utils.misc import Embed
from config import omdb_api_key as api_key

API_URL = 'http://www.omdbapi.com/?t={}&plot=short&apikey={}&y={}'
EMBED_ICON = 'https://cdn4.iconfinder.com/data/icons/planner-color/64/popcorn-movie-time-512.png'

log = logging.getLogger(__name__)

class OMDB:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command(aliases=['imdb'])
    async def omdb(self, ctx, *, query: str):
        """Fetch information about movies/tv series
        Example: <prefix>omdb Movie (year)"""
        year = re.findall("(\d{4})", query)

        if len(year) > 0:
            title = query.rsplit('(')[0].strip()
            year = year[0]
        else:
            year = ""
            title = query

        async with self.bot.session.get(API_URL.format(title, api_key, year)) as r:
            if r.status == 200:
                resp = await r.json()
                if resp['Response'] == "True":
                    em = Embed()
                    if resp['Type'] == 'movie':
                        em.set_author(url='{}'.format('http://www.imdb.com/title/' + resp['imdbID']
                                                      if resp['imdbID'] else 'http://www.imdb.com/'),
                                      name='{} ({})'.format(resp['Title'], resp['Year']), icon_url=EMBED_ICON)
                    elif resp['Type'] == 'series':
                        em.set_author(url='{}'.format('http://www.imdb.com/title/' + resp['imdbID']
                                                      if resp['imdbID'] else 'http://www.imdb.com/'),
                                      name='{} ({} Seasons)'.format(resp['Title'], resp['totalSeasons']
                                      if resp['totalSeasons'] != 'N/A' else 'X'), icon_url=EMBED_ICON)

                    if resp['Poster'] != 'N/A' and len(resp['Poster']) > 10:
                        em.set_thumbnail(url=resp['Poster'])
                    em.add_field(name='Released', value=resp['Released'])
                    em.add_field(name='Rating', value='{} ({} votes)'.format(resp['imdbRating'], resp['imdbVotes']))
                    em.add_field(name='Runtime', value=resp['Runtime'])
                    em.add_field(name='Metascore', value=resp['Metascore'])
                    em.add_field(name='Genres', value=resp['Genre'])
                    em.add_field(name='Actors', value=resp['Actors'])
                    em.add_field(inline=True, name='Plot', value=resp['Plot'])

                    await ctx.send(embed=em)
                else:
                    await ctx.send('```[ERROR] Could not find any information about "{}".```'.format(title.title()))


def setup(bot):
    bot.add_cog(OMDB(bot))
