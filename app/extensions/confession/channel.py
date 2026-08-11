import discord
from discord.ext import commands

CHANNEL_ID = 1525954412424466432

async def fetch_channel(bot: commands.Bot | discord.Client):
    return await bot.fetch_channel(CHANNEL_ID)
