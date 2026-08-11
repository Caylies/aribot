from discord.ext import commands

from .cog import Dev


async def setup(bot: commands.Bot):
    await bot.add_cog(Dev())
