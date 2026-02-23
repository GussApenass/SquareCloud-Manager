import discord
from discord import ui
from base.request.models import SquareErrorModel
from src.components.LayoutView.Profile.LayoutProfileUser import LayoutProfileUser
from src.components.LayoutView.LayoutError import LayoutError
from base import squarecloud_request, emoji

class ProfileMenuButton(ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.menu2
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            data = await squarecloud_request.get_me()

            if isinstance(data, SquareErrorModel):
                code = data.code if data.code else "Erro ao buscar informações do usuário."
                return await interaction.edit_original_response(
                    view=LayoutError(code)
                )


            user = data["user"]

            return await interaction.edit_original_response(
                view=LayoutProfileUser(user)
            )

        except Exception as e:
            return await interaction.edit_original_response(
                view=LayoutError(str(e))
            )
