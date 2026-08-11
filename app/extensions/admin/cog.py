import discord
from discord.ext import commands

from app.core import checks
from models.models.models import BotAdmin, Confession


class Admin(commands.Cog):
    """
    Admin cog for text commands.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def give_admin(self, ctx: commands.Context, user: discord.User):
        """
        Gives a user admin.

        Parameters
        ----------
        user: discord.User
            The user you want to give admin to.
        """
        await BotAdmin.objects.acreate(user_id=user.id)
        await ctx.send(f"Gave admin to {user.name}")

    @commands.command()
    @commands.is_owner()
    async def remove_admin(self, ctx: commands.Context, user: discord.User):
        """
        Removes admin from a user.

        Parameters
        ----------
        user: discord.User
            The user you want to remove admin from.
        """
        try:
            admin = await BotAdmin.objects.aget(user_id=user.id)
        except BotAdmin.DoesNotExist:
            await ctx.send(f"{user.name} is not registered as an admin.")
            return

        await admin.adelete()
        
        await ctx.send(f"Removed admin from {user.name}")

    @commands.command()
    @commands.is_owner()
    async def view_admins(self, ctx: commands.Context):
        """
        Displays all registered admins.
        """
        result = "Admins:\n"

        async for admin in BotAdmin.objects.all():
            user = await self.bot.fetch_user(admin.user_id)

            result += f"- {user.mention}\n"

        await ctx.send(result, allowed_mentions=discord.AllowedMentions.none())

    @commands.command()
    @checks.is_admin()
    async def remove_report(self, ctx: commands.Context, id: str, *, reason: str):
        """
        Removes a report from a confession.

        Parameters
        ----------
        id: str
            The confession ID.
        reason: str
            The reason why you want to remove the report (Required).
        """
        new_id = int(id.replace("#", ""))

        try:
            confession = await Confession.objects.aget(pk=new_id)
        except Confession.DoesNotExist:
            await ctx.send(f"Confession (#{new_id}) could not be found.")
            return

        confession.reports -= 1
        await confession.asave(update_fields=("reports",))
    
        owner = await ctx.bot.fetch_user(ctx.bot.owner_id)

        await owner.send(
            f"{ctx.author.mention} removed a report from "
            f'confession (#{new_id}) with the following reason: "{reason}"'
        )

        await ctx.send(f"Removed one report from confession (#{new_id})")

    @commands.command()
    @checks.is_admin()
    async def view_confession(self, ctx: commands.Context, id: str, *, reason: str):
        """
        Views a confession if it has three or more reports.

        Parameters
        ----------
        id: str
            The confession ID.
        reason: str
            The reason you want to view the confession (Required).
        """
        new_id = int(id.replace("#", ""))

        try:
            confession = await Confession.objects.aget(pk=new_id)
        except Confession.DoesNotExist:
            await ctx.send(f"Confession (#{new_id}) could not be found.")
            return

        if confession.reports < 3:
            await ctx.send("Confessions can only be viewed once they reach or exceed three reports.")
            return

        owner = await ctx.bot.fetch_user(ctx.bot.owner_id)

        await owner.send(f'{ctx.author.mention} viewed confession (#{new_id}) with the following reason: "{reason}"')
        await ctx.author.send(
            f"Confession (#{new_id}) was created by ||<@{confession.user_id}>|| and has {confession.reports:,} reports."
        )
