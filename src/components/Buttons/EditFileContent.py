import discord
from discord import ui
from typing import Dict, Any
from datetime import datetime

from base import emoji, squarecloud_request
from src.components.LayoutView.LayoutError import LayoutError
from src.components.Modais.EditFileContent import EditFileContent

class EditFileContentButton(ui.Button):
    def __init__(self, application_id: str, path: str, archive_path: str, file_name: str):
        self.application_id = application_id
        self.path = path
        self.archive_path = archive_path
        self.file_name = file_name

        super().__init__(
            style=discord.ButtonStyle.primary,
            emoji=emoji.edit_file
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditFileContent(self.application_id, self.path, self.archive_path, self.file_name))
