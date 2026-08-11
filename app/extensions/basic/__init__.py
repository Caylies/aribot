from discord.ext import commands

from .cog import Basic


async def setup(bot: commands.Bot):
    await bot.add_cog(Basic(bot))
