import discord
from base import squarecloud_request, emoji
from src.components.Modais.ConfirmDeletApplicationModal import ConfirmDeletApplicationModal

class DeleteApplicationButton(discord.ui.Button):
    def __init__(self, app_id: str):
        super().__init__(
            emoji=emoji.delete,
            style=discord.ButtonStyle.danger
        )
        self.app_id = app_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ConfirmDeletApplicationModal(self.app_id))