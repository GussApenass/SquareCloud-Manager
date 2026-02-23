import discord
from discord import ui
from typing import Dict, Any
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.Database.ManageOnlyDatabase import ManageOnlyDatabase

class TogglerStartOuPauseDatabase(ui.Button):
    def __init__(self, db_info: Dict[str, Any], db_status: Dict[str, Any]):
        self.db_info = db_info
        self.db_status = db_status

        running = db_status.get("running", False)

        super().__init__(
            emoji=emoji.pause if running else emoji.play,
            style=discord.ButtonStyle.danger if running else discord.ButtonStyle.success
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        db_id = self.db_info.get("id")
        running = self.db_status.get("running", False)

        if running:
            msg = await interaction.followup.send(
                view=LayoutLoading("Parando database..."),
                ephemeral=True
            )

            req = await squarecloud_request.stop_db(db_id)

        else:
            msg = await interaction.followup.send(
                view=LayoutLoading("Iniciando database..."),
                ephemeral=True
            )

            req = await squarecloud_request.start_db(db_id)

        if isinstance(req, SquareErrorModel):
            code = req.code
            msg_error = code if code else "Erro ao alterar estado do database. Verifique se o database já está online ou offline."

            return await msg.edit(view=LayoutError(msg_error))

        # STATUS REQ

        req_status = await squarecloud_request.get_database_status(db_id)

        if isinstance(req_status, SquareErrorModel):
            code = req_status.code
            msg_err = code if code else "Erro ao buscar status do database."

            return await msg.edit(view=LayoutError(msg_err))

        await msg.edit(
            view=LayoutInfo(f"{emoji.check} **|** Ação realizada com sucesso!")
        )

        await interaction.edit_original_response(
            view=ManageOnlyDatabase(self.db_info, req_status)
        )