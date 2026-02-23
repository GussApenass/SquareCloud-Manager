from typing import Any, Dict
import discord
from discord import ui
from base import emoji
from src.components.Modais.Database.EditDatabaseInfoModal import EditDatabaseInfoModal

class EditDatabaseInfo(ui.Button):
    def __init__(self, db_id: str, database_info: Dict[str, Any]):
        self.db_id = db_id
        self.database_info = database_info

        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.pencil
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditDatabaseInfoModal(self.db_id, self.database_info))
