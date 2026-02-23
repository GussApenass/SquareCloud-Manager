import discord
from base import emoji

class LayoutLoading(discord.ui.LayoutView):
  def __init__(self, msg: str):
    super().__init__(timeout=None)

    container1 = discord.ui.Container(
        discord.ui.TextDisplay(content=f"{emoji.loading} - {msg}"),
        accent_colour=discord.Colour(303101),
    )
    self.add_item(container1)