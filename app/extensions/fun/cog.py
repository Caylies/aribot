import discord
from discord import app_commands
from discord.ext import commands

from .utils import fetch_random_fact


class Fun(commands.GroupCog):
    """
    Fun cog.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.cooldown(1, 15, key=lambda i: i.user.id)
    async def fact(self, interaction: discord.Interaction):
        """
        Sends a random fun fact!
        """
        await interaction.response.send_message(fetch_random_fact())
