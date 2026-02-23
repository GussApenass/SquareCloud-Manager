import discord
from base import emoji

class LayoutError(discord.ui.LayoutView):
  def __init__(self, error: str):
    super().__init__(timeout=None)
    
    container1 = discord.ui.Container(
        discord.ui.TextDisplay(content=f"{emoji.xred} ```ansi\n[31m[ERROR][0m -> {error}\n```"),
        accent_colour=discord.Colour(16711680),
    )
    
    self.add_item(container1)