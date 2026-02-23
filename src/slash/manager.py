import discord
from discord.ext import commands
from discord import app_commands
from src.components.LayoutView.InitialLayout import InitialLayout

class Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="manager", description="Gerencie suas aplicações na Square Cloud!")
    @app_commands.allowed_installs(users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=InitialLayout(), ephemeral=True)


async def setup(bot):
    await bot.add_cog(Manager(bot))