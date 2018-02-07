import os
import sys
from discord.ext import commands


class Update:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command()
    async def update_test(self, ctx):
        await ctx.send('```python\n[*] TESTING SELF UPDATE```')
        os.execv(self.bot.base + 'launcher.py', sys.argv)



def setup(bot):
    bot.add_cog(Update(bot))
