import discord
from discord import ui
from base import emoji, squarecloud_request
from src.components.LayoutView.OthersConfiguration import OthersConfiguration

class OutrasConfigsApplication(ui.Button):
    def __init__(self, application_id: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.menu
        )
        self.application_id = application_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_response(
            view=OthersConfiguration(self.application_id)
        )