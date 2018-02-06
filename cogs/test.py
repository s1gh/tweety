from discord.ext import commands
from utils.misc import Embed

class Test:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command()
    async def test(self, ctx):
        em = Embed()
        em.set_author(url='http://www.vg.no', name='Testing')
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Test(bot))