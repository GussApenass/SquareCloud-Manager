import discord
from base import emoji
from src.components.LayoutView.SelectTypeApplication import SelectTypeApplication

class SelectTypeEnterButton(discord.ui.Button):
  def __init__(self):
    super().__init__(
      style=discord.ButtonStyle.gray,
      emoji=emoji.menu2
    )

  async def callback(self, interaction: discord.Interaction):
    await interaction.response.defer()
    
    await interaction.edit_original_response(view=SelectTypeApplication())