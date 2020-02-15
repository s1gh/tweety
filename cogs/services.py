from discord.ext import commands
#from config import plex_token

class Services:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.group()
    async def plex(self, ctx):
        pass

    @plex.command()
    async def status(self, ctx):
        headers = {'X-Plex-Token': 'q7G4PBxAvLQpsBgK7kaJ'}

        async with ctx.typing():
            async with self.bot.session.get('http://plex.tingdal.xyz/library/sections/1/recentlyAdded', headers=headers, timeout=10) as r:
                if r.status == 200:
                    await ctx.send('Plex Server: **ONLINE**')
                else:
                    await ctx.send('Plex Server: **OFFLINE**')


def setup(bot):
    bot.add_cog(Services(bot))