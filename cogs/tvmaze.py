import logging
import datetime
from discord.ext import commands
from utils.misc import Embed

log = logging.getLogger(__name__)

api_url = 'http://api.tvmaze.com/singlesearch/shows?q={}&embed[]=nextepisode&embed[]=previousepisode'

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

                    if ep.previous_episode_name is not None:
                        em.set_footer(text='Previous episode: {} ({})'.format(ep.previous_episode_name,
                                                                              datetime.datetime.strptime(ep.previous_episode_date,
                                                                                                         '%Y-%m-%d').strftime('%d/%m/%Y')))

                    await ctx.send(embed=em)

class Episode:
    def __init__(self, episode):
        self._show_name = episode['name']
        self._runtime = episode['runtime']
        self._genres = episode['genres']
        self._premiered = episode['premiered']
        self._running = True if episode['status'] == 'Running' or episode['status'] == 'In Development' else False
        self._show_poster = episode['image']['medium']
        try:
            self._imdb = 'https://www.imdb.com/title/' + episode['externals']['imdb']
        except KeyError:
            self._imdb = 'https://www.imdb.com/'
        except TypeError:
            self._imdb = 'https://www.imdb.com/'
        try:
            self._network = episode['network']['name']
        except KeyError:
            self._network = 'N/A'

        if self._running:
            self._episode = '{:02d}'.format(int(episode['_embedded']['nextepisode']['number']))
            self._season = '{:02d}'.format(int(episode['_embedded']['nextepisode']['season']))
            self._season_episode = 'S{}E{}'.format(self._season, self._episode)
            self._url = episode['_embedded']['nextepisode']['url']
            self._next_episode = self.air_date(episode['_embedded']['nextepisode']['airdate'])
            self._name = episode['_embedded']['nextepisode']['name']
            try:
                self._summary = episode['_embedded']['nextepisode']['summary'].replace('<p>', '').replace('</p>', '')
            except AttributeError:
                self._summary = 'Not yet available.'
            except KeyError:
                self._summary = 'Not yet available.'

        try:
            self._previous_episode_name = episode['_embedded']['previousepisode']['name']
            self._previous_episode_date = episode['_embedded']['previousepisode']['airdate']
        except Exception:
            self._previous_episode_name = None
            self._previous_episode_date = None

        self._rating = episode['rating']['average']

    def air_date(self, airdate):
        today = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
        ep_date = datetime.datetime.strptime(airdate, '%Y-%m-%d')
        days = ep_date - today

        return (ep_date.strftime('%d/%m/%Y') + ' (' + str(days.days + 1) + ' days)' if days.days > 0 else 'Tomorrow')

    @property
    def previous_episode_name(self):
        return self._previous_episode_name

    @property
    def previous_episode_date(self):
        return self._previous_episode_date

    @property
    def show_name(self):
        return self._show_name

    @property
    def runtime(self):
        return self._runtime

    @property
    def genres(self):
        return self._genres

    @property
    def premiered(self):
        return self._premiered

    @property
    def running(self):
        return self._running

    @property
    def show_poster(self):
        return self._show_poster

    @property
    def summary(self):
        return self._summary

    @property
    def imdb(self):
        return self._imdb

    @property
    def network(self):
        return self._network

    @property
    def url(self):
        return self._url

    @property
    def season_episode(self):
        return self._season_episode

    @property
    def rating(self):
        return self._rating

    @property
    def next_episode(self):
        return self._next_episode

    @property
    def name(self):
        return self._name

    @property
    def season(self):
        return self._season

    @property
    def episode(self):
        return self._episode


def setup(bot):
    bot.add_cog(Tvmaze(bot))