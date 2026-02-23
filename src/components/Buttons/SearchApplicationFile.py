import discord
from base import emoji
from src.components.Modais.PathSearchModal import PathSearchModal

class SearchApplicationFile(discord.ui.Button):
  def __init__(self, application_id: str, path: str):
    super().__init__(
      style=discord.ButtonStyle.gray,
      emoji=emoji.search
    )
    self.application_id = application_id
    self.path = path

  async def callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(PathSearchModal(self.application_id, self.path))