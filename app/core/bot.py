import os

import discord
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="ari.", intents=discord.Intents.all())
        self.owner_id = 743877445723095071

    async def setup_hook(self):
        from ..extensions.confession.components import ConfessionView

        self.add_view(ConfessionView())

        for extension in [ext for ext in os.listdir("app/extensions") if ext not in ["__init__.py", "__pycache__"]]:
            try:
                await self.load_extension(f"app.extensions.{extension}")
            except Exception as error:
                print(f"Failed to load '{extension}' extension: {error}")
                continue
            else:
                print(f"Loaded '{extension}' extension")

        await self.tree.sync()

        print("Synced tree!")
