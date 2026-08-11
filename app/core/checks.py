from discord.ext import commands

from models.models.models import BotAdmin


def is_admin():
    async def predicate(ctx: commands.Context) -> bool:
        return await BotAdmin.objects.filter(user_id=ctx.author.id).aexists()

    return commands.check(predicate)
