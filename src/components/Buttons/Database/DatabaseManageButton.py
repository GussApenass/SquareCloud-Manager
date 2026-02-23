import discord
from discord import ui
from base.request.models import SquareErrorModel
from src.components.LayoutView.Database.ListDatabases import ListDatabases
from src.components.LayoutView.LayoutError import LayoutError
from base import squarecloud_request, emoji

class DatabaseManageButton(ui.Button):
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
                code = data.code if data.code else "Erro ao buscar databases."
                return await interaction.edit_original_response(
                    view=LayoutError(code)
                )

            databases = data["databases"]

            return await interaction.edit_original_response(
                view=ListDatabases(databases)
            )

        except Exception as e:
            return await interaction.edit_original_response(
                view=LayoutError(str(e))
            )
