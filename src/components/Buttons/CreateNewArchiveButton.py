import discord
from base import emoji
from src.components.Modais.CreateNewArchive import CreateNewArchive

class CreateNewArchiveButton(discord.ui.Button):
  def __init__(self, application_id: str):
    super().__init__(
      label="Criar novo Arquivo",
      style=discord.ButtonStyle.gray,
      emoji=emoji.file
    )
    self.application_id = application_id

  async def callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(CreateNewArchive(self.application_id))