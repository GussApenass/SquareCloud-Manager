from typing import Any, Dict
import discord
from discord import ui
from base.request.models import SquareErrorModel
from src.components.LayoutView.Profile.LayoutProfileUser import LayoutProfileUser
from src.components.LayoutView.LayoutError import LayoutError
from base import emoji

class ShowEmailButton(ui.Button):
    def __init__(self, user_info: Dict[str, Any], show_email: bool):

        if show_email:
            emoji_ = emoji.eye_closed
        else:
            emoji_ = emoji.eye

        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji_
        )
        self.user_info = user_info
        self.show_email = show_email

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if self.show_email:
            await interaction.edit_original_response(
                view=LayoutProfileUser(self.user_info, False)
            )
        else:
            await interaction.edit_original_response(
                view=LayoutProfileUser(self.user_info, True)
            )