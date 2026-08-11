import discord
from discord.ext import commands


class Basic(commands.Cog):
    """
    Base cog for text commands.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def synctree(self, ctx: commands.Context, guild_id: int | None = None):
        """
        Syncs Discord application commands.

        Parameters
        ----------
        guild_id: int | None
            The guild that will be synced.
        """
        message = await ctx.send("Syncing tree...")

        if guild_id is None:
            await self.bot.tree.sync()
        else:
            await self.bot.tree.sync(guild=discord.Object(id=guild_id))

        await message.reply("Synced tree!")

    async def reload_extension(self, package: str, *, with_prefix=False):
        try:
            try:
                await self.bot.reload_extension(package)
            except commands.ExtensionNotLoaded:
                await self.bot.load_extension(package)
        except commands.ExtensionNotFound:
            if not with_prefix:
                await self.reload_extension("app.extensions." + package, with_prefix=True)
                return
            raise

    @commands.command()
    @commands.is_owner()
    async def reloadext(self, ctx: commands.Context, extension: str):
        """
        Reloads an extension.

        Parameters
        ----------
        extension: str
            The extension that will be reloaded.
        """
        try:
            await self.reload_extension(extension)
        except commands.ExtensionNotFound:
            await ctx.send(f"The '{extension}' extension could not be found.")
        except Exception as error:
            await ctx.send(f"Failed to reload the '{extension}' extension.")
            print(error)
        else:
            await ctx.send(f"Successfully reloaded the '{extension}' extension!")

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """
        Replies with "pong"!
        """
        await ctx.reply("Pong!")
