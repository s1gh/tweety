import logging
from discord.ext import commands
from utils.database import Database
from utils.misc import Embed
from datetime import datetime
from asyncpg import exceptions

EMBED_THUMBNAIL = 'http://www.guibingzhuche.com/data/out/269/1720508.png'

log = logging.getLogger(__name__)

class Quotes(Database):
    def __init__(self, tweety):
        self.bot = tweety
        super().__init__(self.bot.pool)

    @commands.group(invoke_without_command=True)
    async def quote(self, ctx, user: str):
        """Handles quotes (adding, viewing etc.)"""
        try:
            quote = await self.query('SELECT COUNT(*) OVER (), q.* '
                                     'FROM quotes q '
                                     'WHERE q.author = $1 AND server_id = $2 '
                                     'ORDER BY random() LIMIT 1', [user.lower(), ctx.guild.id])
            em = Embed()
            em.add_field(name=quote[0]['author'].title(), value='*"{}"*'.format(quote[0]['quote'].capitalize()))
            em.set_thumbnail(url=EMBED_THUMBNAIL)
            em.set_footer(text='Added: {} • Quotes: {} • ID: {}'.format(quote[0]['timestamp'].strftime('%d.%m.%y %H:%M:%S'),
                                                                       quote[0]['count'], quote[0]['id']))
        except IndexError:
            await ctx.send('```[Info] {} doesn\'t have a quote, yet. Maybe you should add one?```'.format(user.title()))
        else:
            await ctx.send(embed=em)

    @quote.command(aliases=['create'])
    async def add(self, ctx, user: str, *, quote: str):
        try:
            params = [
                ctx.author.id,
                ctx.guild.id,
                quote,
                user.lower(),
                datetime.now()
            ]
            ret = await self.query('INSERT INTO quotes (added_by, server_id, quote, author, timestamp) '
                                        'VALUES ($1, $2, $3, $4, $5) RETURNING id', params)
        except exceptions.UniqueViolationError:
            await ctx.send('```[ERROR] This quote already exist.```')
        except Exception as err:
            log.error(err)
        else:
            await ctx.send('```[INFO] Quote added to database successfully - ID: {}```'.format(ret[0]['id']))

    @quote.command(aliases=['change','update'])
    async def edit(self, ctx, quote_id: int, *, new_quote: str):
        try:
            params = [
                new_quote,
                quote_id,
                ctx.author.id
            ]

            ret = await self.query('UPDATE quotes x '
                                   'SET quote = $1 '
                                   'FROM quotes y '
                                   'WHERE x.id = y.id AND x.id = $2 AND x.added_by = $3 '
                                   'RETURNING y.quote as old_quote', params)
            if ret is None:
                await ctx.send('```[ERROR] Could not update quote. Are you sure you own this quote?```')
            else:
                await ctx.send('```[INFO] Quote with ID {} updated successfully.\n"{}" → "{}"```'.format(quote_id, ret[0]['old_quote'], new_quote))
        except exceptions.UniqueViolationError:
            await ctx.send('```[ERROR] This quote already exist.```')
        except IndexError:
            await ctx.send('```Quote with ID {} does not exist.```'.format(quote_id))
        except Exception as err:
            log.error(err)


    @quote.command(aliases=['remove', 'purge'])
    async def delete(self, ctx, id: int):
        try:
            params = [
                id,
                ctx.author.id
            ]
            ret = await self.execute('DELETE FROM quotes WHERE id = $1 AND added_by = $2', params)

            if int(ret[-1:]):
                await ctx.send('```[INFO] Quote with ID {} deleted successfully.```'.format(id))
            else:
                await ctx.send('```[ERROR] Could not delete quote with ID {}. You\'re not the owner of this quote.```')
        except Exception as err:
            log.error(err)


def setup(bot):
    bot.add_cog(Quotes(bot))