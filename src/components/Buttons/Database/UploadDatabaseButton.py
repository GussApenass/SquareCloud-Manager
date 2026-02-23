import discord
from base import emoji
from src.components.Modais.Database.UploadDatabaseModal import UploadDatabaseModal

class UploadDatabaseButton(discord.ui.Button):
  def __init__(self):
    super().__init__(
      label="Criar Database",
      style=discord.ButtonStyle.gray,
      emoji=emoji.upload
    )

  async def callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(UploadDatabaseModal())