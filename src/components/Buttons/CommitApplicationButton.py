import discord
from base import emoji
from src.components.Modais.CommitModal import CommitApplication

class CommitApplicationButton(discord.ui.Button):
  def __init__(self, application_id: str):
    super().__init__(
      style=discord.ButtonStyle.gray,
      emoji=emoji.upload
    )
    self.application_id = application_id

  async def callback(self, interaction: discord.Interaction):
    await interaction.response.send_modal(CommitApplication(self.application_id))