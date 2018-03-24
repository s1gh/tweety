import markovify
import discord
import logging
from discord.ext import commands
from utils.database import Database

log = logging.getLogger(__name__)

class Markov(Database):
    def __init__(self, tweety):
        self.bot = tweety
        super().__init__(self.bot.pool)

    @commands.command()
    async def markov(self, ctx, *, user: discord.Member=None):
        try:
            if user is None:
                query = 'SELECT message FROM chatlog'
            else:
                query = 'SELECT message FROM chatlog WHERE member_id = $1'

            txt = await self.query(query, [] if user is None else [user.id])
            model = markovify.NewlineText('\n'.join(x['message'] for x in txt), state_size=3 if user is None else 2)
            sentence = model.make_sentence(tries=250 if user is None else 500)
        except Exception as err:
            log.error(err)
        else:
            await ctx.send(sentence)

    @markov.error
    async def markov_error(self, ctx, error):
        await ctx.send('```[ERROR] {}.```'.format(error))


def setup(bot):
    bot.add_cog(Markov(bot))