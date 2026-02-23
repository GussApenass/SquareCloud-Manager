import discord
from base import emoji
from src.components.Modais.Database.ConfirmDeletDatabaseModal import ConfirmDeletDatabaseModal

class DeleteDatabaseButton(discord.ui.Button):
    def __init__(self, db_id: str):
        super().__init__(
            emoji=emoji.delete,
            style=discord.ButtonStyle.danger
        )
        self.db_id = db_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ConfirmDeletDatabaseModal(self.db_id))