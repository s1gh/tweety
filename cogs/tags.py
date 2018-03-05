import difflib
import logging
from datetime import datetime
from discord.ext import commands
from utils.database import Database
from asyncpg import exceptions

log = logging.getLogger(__name__)

class Tags(Database):
    def __init__(self, tweety):
        self.bot = tweety
        super().__init__(self.bot.pool)

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, tag: str):
        lookup = tag.lower()

        try:
            tag = await self.query('SELECT tag_content, server_id FROM tags WHERE tag_id = $1 LIMIT 1', [lookup,])
        except Exception as err:
            log.error(err)
        else:
            if len(tag) == 1:
                if tag[0]['server_id'] == ctx.message.guild.id:
                    await ctx.send(tag[0]['tag_content'])
                else:
                    await ctx.send('```[ERROR] {}```'.format('No tag with that name exist.'))

    @tag.command(aliases=['create'])
    async def add(self, ctx, tag_id: str, *, tag_content: str):
        params = [
            ctx.message.author.id,
            tag_id.lower(),
            tag_content.lower(),
            datetime.now(),
            ctx.message.guild.id,
        ]

        try:
            await self.execute('INSERT INTO tags (member_id, tag_id, tag_content, timestamp, server_id) '
                              'VALUES ($1, $2, $3, $4, $5)', params)
        except exceptions.UniqueViolationError:
            await ctx.send('```[ERROR] {}```'.format('A tag with that name already exist.'))
        except Exception as err:
            log.error(err)
        else:
            await ctx.send('```[INFO] {}```'.format('Tag successfully created.'))

    @tag.command(alises=['update', 'change'])
    async def edit(self, ctx, tag_id: str, *, tag_content: str):
        params = [
            tag_content,
            ctx.message.author.id,
            tag_id,
        ]

        try:
            ret = await self.execute('UPDATE tags SET tag_content = $1 WHERE member_id = $2 AND tag_id = $3', params)
            if int(ret[-1:]):
                await ctx.send('```[INFO] {}```'.format('Successfully modified the tag.'))
        except Exception as err:
            log.error(err)

    @tag.command(aliases=['rm', 'remove'])
    async def delete(self, ctx, tag_id: str):
        params = [
            ctx.message.author.id,
            tag_id,
        ]
        try:
            ret = await self.execute('DELETE FROM tags WHERE member_id = $1 AND tag_id = $2', params)
            if int(ret[-1:]):
                await ctx.send('```[INFO] {}```'.format('Tag successfully removed.'))
        except Exception as err:
            log.error(err)

    @tag.error
    @edit.error
    @add.error
    async def tag_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('```[ERROR] {}```'.format(error))


def setup(bot):
    bot.add_cog(Tags(bot))