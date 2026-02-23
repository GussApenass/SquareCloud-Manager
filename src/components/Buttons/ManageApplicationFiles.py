import discord
from discord import ui
from base import emoji
from src.components.Modais.PathSearchModal import PathSearchModal

class ManageApplicationFiles(ui.Button):
    def __init__(self, application_id: str):
        self.application_id = application_id

        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.menu2
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(PathSearchModal(self.application_id))
