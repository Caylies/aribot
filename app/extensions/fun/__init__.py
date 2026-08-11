from discord.ext import commands

from .cog import Fun


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
