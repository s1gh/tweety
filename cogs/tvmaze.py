import logging
from discord.ext import commands
from utils.misc import Episode, Embed

log = logging.getLogger(__name__)

api_url = 'http://api.tvmaze.com/singlesearch/shows?q={}&embed=nextepisode'


class Tvmaze:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command(aliases=['ep'])
    async def nextepisode(self, ctx, *, show: str):
        async with self.bot.session.get(api_url.format(show)) as r:
            if r.status == 200:
                ep = Episode(await r.json())

                if not ep.running:
                    await ctx.send('``[INFO] Show has ended or been cancelled.``')
                else:
                    em = Embed(url=ep.url, title='S{}E{} - {}'.format(ep.season, ep.episode, ep.name))
                    em.set_author(name=ep.show_name, url=ep.imdb)
                    em.set_thumbnail(url=ep.show_poster)
                    em.add_field(name='Show Rating', value='{}/10'.format(ep.rating), inline=True)
                    em.add_field(name='Network', value=ep.network, inline=True)
                    em.add_field(name='Next Episode', value=ep.next_episode, inline=True)
                    em.add_field(name='Runtime', value='{} Minutes'.format(ep.runtime), inline=True)
                    em.add_field(name='Episode Summary', value=ep.summary, inline=False)

                    await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Tvmaze(bot))