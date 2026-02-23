from typing import Any, Dict
import discord
from discord import ui
from base import squarecloud_request, emoji
from src.components.Modais.ConfirmDeleteApplicationFile import ConfirmDeleteFileModal

class DeleteApplicationFile(ui.Button):
    def __init__(self, app_id: str, path: str):
        super().__init__(
            style=discord.ButtonStyle.danger,
            emoji=emoji.delete
        )
        self.app_id = app_id
        self.path = path

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ConfirmDeleteFileModal(self.app_id, self.path))
