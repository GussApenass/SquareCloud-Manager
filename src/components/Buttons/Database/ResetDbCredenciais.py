import discord
from discord import ui
from base.request.models import SquareErrorModel
from base import emoji, squarecloud_request
from src.components.LayoutView.LayoutError import LayoutError
from src.components.Modais.Database.ResetDbCredenciaisModal import ResetDbCredenciaisModal

class ResetDbCredenciais(ui.Button):
    def __init__(self, db_id: str):
        self.db_id = db_id

        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.credencial
        )

    async def callback(self, interaction: discord.Interaction):
        db_info = await squarecloud_request.get_database(self.db_id)

        if isinstance(db_info, SquareErrorModel):
            code = db_info.code
            msg = code if code else "Erro ao obter informações do banco de dados."

            return await interaction.response.send_message(
                view=LayoutError(msg),
                ephemeral=True
            )

        await interaction.response.send_modal(ResetDbCredenciaisModal(db_info, self.db_id))
        