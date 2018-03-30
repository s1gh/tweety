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
        """Uses a markov chain to create a sentence based on the chat history for this guild."""
        async with ctx.typing():
            try:
                if user is None:
                    query = 'SELECT message FROM chatlog'
                else:
                    query = 'SELECT message FROM chatlog WHERE member_id = $1'

                txt = await self.query(query, [] if user is None else [user.id])
                model = markovify.NewlineText('\n'.join(x['message'] for x in txt), state_size=3 if user is None else 2)
                sentence = model.make_sentence(tries=300 if user is None else 600)
            except Exception as err:
                log.error(err)
            else:
                await ctx.send(sentence)

    @markov.error
    async def markov_error(self, ctx, error):
        log.error(error)


def setup(bot):
    bot.add_cog(Markov(bot))