from discord.ext import commands

class Testing:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command()
    async def test_update_function(self, ctx):
        await ctx.send('This function was pulled from Github. Everything is working! :)')


def setup(bot):
    bot.add_cog(Testing(bot))