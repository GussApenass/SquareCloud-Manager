from typing import Any, Dict
import discord
from discord import ui
from src.components.LayoutView.ListApplications import ListApplications
from src.components.LayoutView.LayoutError import LayoutError
from base import squarecloud_request, emoji
from src.components.Modais.MoveAppFileModal import MoveAppFile

class MoveApplicationFile(ui.Button):
    def __init__(self, app_id: str, path: str, file_data: Dict[str, Any]):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.move
        )
        self.app_id = app_id
        self.path = path
        self.file_data = file_data

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(MoveAppFile(self.app_id, self.path, self.file_data))
