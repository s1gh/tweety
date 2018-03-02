import json
import logging
from copy import copy
from discord.ext import commands

log = logging.getLogger(__name__)

class Alias:
    def __init__(self, tweety):
        self.bot = tweety
        self.alias_map = {}
        try:
            with open('data/{}/{}'.format(self.bot.base, 'alias_map.json'), 'r') as f:
                self.alias_map = json.load(f)
        except IOError:
            pass
        except json.decoder.JSONDecodeError as err:
            log.error('JSON: {}'.format(err))

    @commands.group()
    async def alias(self, ctx):  # !alias add <alias> <command (and args) without prefix>
        pass

    @alias.command()
    async def add(self, ctx, alias_name, *, command):
        uid = str(ctx.message.author.id)
        prefix = await self.bot.get_prefix(ctx)

        if not alias_name.startswith(tuple(prefix)) and not command.startswith(tuple(prefix)):
            try:
                if not uid in self.alias_map:
                    self.alias_map[uid] = {alias_name:command}
                else:
                    self.alias_map[uid].update({alias_name:command})

                with open('data/{}/{}'.format(self.bot.base, 'alias_map.json'), 'w') as f:
                    json.dump(self.alias_map, f)
            except IOError:
                log.error('Could not write to alias_map.json.')
        else:
            await ctx.send('```[ERROR] Alias or the command to execute can not start with a bot prefix.```')

    @alias.command(aliases=['del', 'delete', 'rm'])
    async def remove(self, ctx, alias_name):
        uid = str(ctx.message.author.id)

        try:
            del self.alias_map[uid][alias_name]
            await ctx.send('```[INFO] Alias "{}" removed.```'.format(alias_name))
        except KeyError:
            await ctx.send('```[ERROR] Could not find alias "{}".```'.format(alias_name))

    @alias.command()
    async def edit(self, ctx, alias_name, *, command):
        uid = str(ctx.message.author.id)

        if uid in self.alias_map:
            if alias_name in self.alias_map[uid]:
                self.alias_map[uid][alias_name] = command
            else:
                await ctx.send('```[ERROR] Could not find alias "{}".```'.format(alias_name))
        else:
            await ctx.send('```[ERROR] You have no registered aliases.```')

    @alias.command(name='list')  # →
    async def _list(self, ctx):
        uid = str(ctx.message.author.id)

        if uid in self.alias_map:
            prefix = await self.bot.get_prefix(ctx)
            aliases = self.alias_map[uid]
            msg = '\n'.join('{} → {}{}'.format(k, prefix[0], v) for k, v in aliases.items())

            await ctx.send('**Aliases for {}**\n```{}```'.format(ctx.author.name, msg))
        else:
            await ctx.send('```[INFO] {}```'.format('You have not created any aliases yet.'))

    @alias.error
    @add.error
    @remove.error
    @edit.error
    async def alias_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('```[ERROR] {}```'.format(error))


    async def on_message(self, message):
        if message.author.bot:
            return

        if str(message.author.id) in self.alias_map:
            if message.content in self.alias_map[str(message.author.id)]:
                prefix = await self.bot.get_prefix(message)

                cmd = self.alias_map[str(message.author.id)][message.content]
                msg = copy(message)
                msg.content = '{}{}'.format(prefix[0], cmd)

                await self.bot.process_commands(msg)


def setup(bot):
    bot.add_cog(Alias(bot))