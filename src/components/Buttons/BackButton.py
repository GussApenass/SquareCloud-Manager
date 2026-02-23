import discord
from base import emoji
from typing import Callable, Any, Coroutine

CallbackType = Callable[[discord.Interaction], Coroutine[Any, Any, Any]]

class BackButton(discord.ui.Button):
  def __init__(self, callback_func: CallbackType):
    super().__init__(
      emoji=emoji.back,
      style=discord.ButtonStyle.secondary
    )
    self.callback_func = callback_func

  async def callback(self, interaction: discord.Interaction):
    await self.callback_func(interaction)