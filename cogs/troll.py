import logging
from math import ceil
from discord.ext import commands

api_url = 'http://pugme.herokuapp.com/bomb?count={}'

log = logging.getLogger(__name__)


class Troll:
    def __init__(self, tweety):
        self.bot = tweety

    @commands.command()
    @commands.cooldown(1, 180, commands.BucketType.guild)  # Can only be used 1 time per 180 seconds (server limit)
    async def pugbomb(self, ctx, count: int = 3):
        """Most useless plugin ever. Troll other members of this guild"""
        if count > 20:
            raise commands.CheckFailure
        elif not isinstance(count, int):
            raise commands.BadArgument
        async with self.bot.session.get(api_url.format(count)) as r:
            if r.status == 200:
                data = await r.json()
                for pug in data['pugs']:
                    await ctx.send('https://{}'.format(pug.split('.', 1)[1]))

    @pugbomb.error
    async def pugbomb_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            log.warning('User "{}" is being rate limited ({}).'.format(ctx.message.author, ctx.command))
            await ctx.send('```[INFO] This command is on cooldown, please retry in {} seconds.```'.format(ceil(error.retry_after)))
        elif isinstance(error, commands.CheckFailure):
            ctx.command.reset_cooldown(ctx)
            await ctx.send('```[ERROR] {}```'.format('Whoah, that\'s alot of pugs. Try a lower number.'))
        elif isinstance(error, commands.BadArgument):
            ctx.command.reset_cooldown(ctx)
            await ctx.send('```[ERROR] {}```'.format('Bad argument. Expected an integer.'))


def setup(bot):
    bot.add_cog(Troll(bot))