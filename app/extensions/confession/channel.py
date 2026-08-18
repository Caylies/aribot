import discord
from discord.ext import commands

CHANNEL_ID = 1539107964193873991

async def fetch_channel(bot: commands.Bot | discord.Client):
    return await bot.fetch_channel(CHANNEL_ID)
