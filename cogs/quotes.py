from discord.ext import commands
from utils.database import Database
from utils.misc import Embed

EMBED_THUMBNAIL = 'https://polybius.io/static/homepage/images/2015_quote_marks_close.png'

class Quotes(Database):
    def __init__(self, tweety):
        self.bot = tweety
        super().__init__(self.bot.pool)

    @commands.group()
    async def quote(self, ctx, user: str):
        try:
            quote = await self.query('SELECT COUNT(*) OVER (), q.* '
                                     'FROM quotes q '
                                     'WHERE q.author = $1 AND server_id = $2 '
                                     'ORDER BY random() LIMIT 1', [user, ctx.guild.id])
            em = Embed()
            em.add_field(name=quote[0]['author'].title(), value='*"{}"*'.format(quote[0]['quote'].capitalize()))
            em.set_thumbnail(url=EMBED_THUMBNAIL)
            em.set_footer(text='Added {} | Number of quotes: {}'.format(quote[0]['timestamp'], quote[0]['count']))
        except IndexError:
            await ctx.send('```[Info] {} doesn\'t have a quote, yet. Maybe you should add one?```'.format(user.title()))
        else:
            await ctx.send(embed=em)

    @quote.command()
    async def add(self, ctx):
        pass

    @quote.command()
    async def edit(self, ctx):
        pass

    @quote.command()
    async def delete(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Quotes(bot))