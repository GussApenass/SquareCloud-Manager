import discord
from base import emoji
from src.components.Modais.UploadModal import UploadApplication

class UploadApplicationButton(discord.ui.Button):
  def __init__(self):
    super().__init__(
      label="Enviar Aplicação",
      style=discord.ButtonStyle.gray
    )

  async def callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(UploadApplication())