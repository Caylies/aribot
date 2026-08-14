import discord
from discord import app_commands
from discord.ext import commands

from models.models.models import BotAdmin, Confession

from .channel import fetch_channel
from .components import ConfessionView, ConfessionModal, sync_confession_message
from .likes import toggle_like
from .utils import format_id


class Confessions(commands.GroupCog, name="confession"):
    """
    Durr commands.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reports: dict[int, set[int]] = {}

    @app_commands.command()
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def report(self, interaction: discord.Interaction, id: str):
        """
        Reports a confession. If a confession recieves three reports, it will be reviewed by a moderator.

        Parameters
        ----------
        id: str
            The confession ID.
        """
        await interaction.response.defer(thinking=True, ephemeral=True)

        new_id = format_id(id)

        if not new_id:
            await interaction.followup.send("Confession ID is invalid.")
            return

        if new_id not in self.reports:
            self.reports[new_id] = set()

        if interaction.user.id in self.reports[new_id]:
            await interaction.followup.send("You already reported this confession.")
            return

        self.reports[new_id].add(interaction.user.id)

        try:
            confession = await Confession.objects.aget(pk=new_id)
        except Confession.DoesNotExist:
            await interaction.followup.send(f"Confession (#{new_id}) could not be found.")
            return

        confession.reports += 1

        await confession.asave(update_fields=("reports",))

        if confession.reports == 3:
            async for admin in BotAdmin.objects.all():
                user = await self.bot.fetch_user(admin.user_id)
                await user.send(view=await ConfessionView.from_confession(confession, report_display=True))

        channel = await fetch_channel(self.bot)
        await sync_confession_message(channel, confession)

        plural = "" if confession.reports == 1 else "s"

        await interaction.followup.send(
            f"Confession (#{new_id}) has been reported {confession.reports:,} time{plural}."
        )

    @app_commands.command()
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def like(self, interaction: discord.Interaction, id: str):
        """
        Adds or removes a like from a confession.

        Parameters
        ----------
        id: str
            The confession ID.
        """
        await interaction.response.defer(thinking=True, ephemeral=True)

        new_id = format_id(id)

        if not new_id:
            await interaction.followup.send("Confession ID is invalid.")
            return

        try:
            confession = await Confession.objects.aget(pk=new_id)
        except Confession.DoesNotExist:
            await interaction.followup.send(f"Confession (#{new_id}) could not be found.")
            return

        if not confession.message_id:
            await interaction.response.send_message(
                f"Confession (#{new_id}) is a legacy confession and cannot be liked.",
                ephemeral=True
            )
            return

        liked = await toggle_like(interaction.user.id, confession)

        await interaction.followup.send(f"Like {'added' if liked else 'removed'}.")

        confession = await Confession.objects.aget(pk=new_id)

        channel = await fetch_channel(self.bot)
        await sync_confession_message(channel, confession)

    @app_commands.command()
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.user.id)
    async def sync(self, interaction: discord.Interaction):
        """
        Syncs the last confession message. If confession buttons aren't working, this command will fix it.
        """
        await interaction.response.defer(thinking=True, ephemeral=True)

        channel = await fetch_channel(self.bot)

        if not channel:
            await interaction.followup.send("Confession channel could not be found.")
            return

        confession = await Confession.objects.alast()

        if not confession:
            await interaction.followup.send("No confessions have been sent yet.")
            return

        await sync_confession_message(channel, confession)
        await interaction.followup.send("Confession message synced!")

    @app_commands.command()
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def send(self, interaction: discord.Interaction, reply_id: str | None = None):
        """
        Sends an anonymous confession.

        Parameters
        ----------
        reply_id: str | None
            The confession you want to reply to based on the confession's ID.
        """
        reply_confession = None

        if reply_id:
            new_id = format_id(reply_id)

            if not new_id:
                await interaction.response.send_message(
                    "Reply confession ID is invalid. "
                    "If you want to send a standalone confession, leave the \"reply_id\" field blank.",
                    ephemeral=True
                )
                return

            try:
                reply_confession = await Confession.objects.aget(pk=new_id)
            except Confession.DoesNotExist:
                await interaction.response.send_message(f"Confession (#{new_id}) could not be found.", ephemeral=True)
                return

            if not reply_confession.message_id:
                await interaction.response.send_message(
                    f"Confession (#{new_id}) is a legacy confession and cannot be replied to.",
                    ephemeral=True
                )
                return

        await interaction.response.send_modal(ConfessionModal(reply_confession=reply_confession))
