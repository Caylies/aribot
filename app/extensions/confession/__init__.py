from discord.ext import commands

from .cog import Confessions



async def setup(bot: commands.Bot):
    await bot.add_cog(Confessions(bot))
