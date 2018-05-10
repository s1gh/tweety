import logging
import time
import discord
from utils.database import Database
from datetime import datetime, timedelta
from discord.ext import commands
from utils.misc import Embed

log = logging.getLogger(__name__)

class Stats(Database):
    def __init__(self, tweety):
        super().__init__(tweety.pool)
        self.bot = tweety
        self.tracking_map = {}  # {'member_id': { 'status': 'PUBg', 'time_started': 23232323223, 'server_id': 32123123 } }

    @commands.group(aliases=['gamestats', 'games', 'stats'])
    async def analytics(self, ctx):
        """Fetch information about the most popular games etc."""
        pass

    @analytics.command()
    async def topgames(self, ctx):
        try:
            res = await self.query('SELECT game, SUM(game_time) '
                                   'FROM games '
                                   'WHERE (timestamp >= date_trunc(\'week\', current_date)) '
                                   'AND server_id = $1 '
                                   'GROUP BY game '
                                   'ORDER BY sum DESC LIMIT 5', [ctx.guild.id])
        except Exception as err:
            log.error(err)
        else:
            em = Embed(description='Most popular games this week based on combined in-game time.')
            em.set_thumbnail(url='https://images.vexels.com/media/users/3/128895/isolated/preview/f9298b663ad1e671680cad2ed70b20c3-timer-reload-flat-icon-by-vexels.png')
            em.set_author(name='Top Games This Week')

            for num in range(len(res)):
                em.add_field(name='{}. {}'.format(num+1, res[num]['game']),
                             value=str(timedelta(seconds=res[num]['sum'])), inline=False)

            await ctx.send(embed=em)

    @analytics.command()
    async def leaderboards(self, ctx, time: str = 'week'):
        try:
            res = await self.query('SELECT member_id, SUM(game_time) '
                                   'FROM games '
                                   'WHERE (timestamp >= date_trunc(\'{}\', CURRENT_TIMESTAMP)) '
                                   'AND server_id = $1 '
                                   'GROUP BY member_id '
                                   'ORDER BY sum DESC LIMIT 10'.format(time), [ctx.guild.id])
        except Exception as err:
            log.error(err)
        else:
            place = 1
            em = Embed(description='Players with the highest in-game time this {}.'.format(time))
            em.set_thumbnail(url='https://cdn1.iconfinder.com/data/icons/hawcons/32/699902-icon-34-award-128.png')
            em.set_author(name='Weekly In-game Time')
            for data in res:
                member = discord.utils.get(ctx.guild.members, id=data['member_id'])
                em.add_field(name='{}. {}'.format(place, member.name), value=str(timedelta(seconds=data['sum'])))
                place += 1
            await ctx.send(embed=em)

    @analytics.command()
    async def spotify(self, ctx):
        try:
            res = await self.query('SELECT member_id, SUM(game_time) '
                                   'FROM games '
                                   'WHERE game=$1 '
                                   'AND (timestamp >= date_trunc(\'week\', CURRENT_TIMESTAMP)) '
                                   'GROUP BY member_id '
                                   'ORDER BY sum DESC', ['Spotify'])
        except Exception as err:
            log.error(err)
        else:
            place = 1
            em = Embed(description='Members with the highest Spotify usage this week.')
            em.set_thumbnail(url='https://images.vexels.com/media/users/3/137413/isolated/preview/4acb8e52632aa9b7c874b878eaf02bc4-spotify-icon-logo-by-vexels.png')
            em.set_author(name='Weeky Spotify Usage')
            for data in res:
                member = discord.utils.get(ctx.guild.members, id=data['member_id'])

                em.add_field(name='{}. {}'.format(place, member.name), value=str(timedelta(seconds=data['sum'])))
                place += 1
            await ctx.send(embed=em)

    @analytics.command()
    async def history(self, ctx):
        try:
            res = await self.query('SELECT DISTINCT game '
                                   'FROM games ', [])
        except Exception as err:
            log.error(err)
        else:
            games = [x['game'] for x in res]
            await ctx.send('**Games on Record**\n```{}\n\nTotal: {}```'.format(', '.join(games), len(games)))

    async def on_member_update(self, before, after):
        try:
            if after.activity is not None and after.id not in self.tracking_map:
                self.tracking_map[after.id] = {'status': str(after.activity), 'time_started': int(time.time()),
                                               'server_id': before.guild.id}

                params = [
                    before.id,
                    datetime.now(),
                    before.guild.id
                ]
                await self.execute('INSERT INTO members (member_id, last_played, server_id) '
                                   'VALUES ($1, $2, $3) '
                                   'ON CONFLICT (member_id, server_id) DO '
                                   'UPDATE SET last_played = \'{}\''.format(datetime.now()), params)
            elif after.activity is None:
                play_time = int(time.time()) - self.tracking_map[before.id]['time_started']

                params = [
                    before.id,
                    before.guild.id,
                    self.tracking_map[before.id]['status'],
                    play_time,
                    datetime.now()
                ]

                try:
                    await self.execute('INSERT INTO games (member_id, server_id, game, game_time, timestamp) '
                                       'VALUES ($1, $2, $3, $4, $5)', params)
                except Exception as err:
                    log.error(err)
                else:
                    del self.tracking_map[after.id]  # Remove old tracking data since the member is not playing anymore.
        except KeyError:
            return

def setup(bot):
    bot.add_cog(Stats(bot))
