import discord
from discord import ui
from base import emoji, squarecloud_request
from src.components.LayoutView.Database.OthersConfigs.OthersConfigsLayout import OthersConfigsLayout

class OthersConfigsDatabases(ui.Button):
    def __init__(self, db_id: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.menu
        )
        self.db_id = db_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.edit_original_response(view=OthersConfigsLayout(self.db_id))