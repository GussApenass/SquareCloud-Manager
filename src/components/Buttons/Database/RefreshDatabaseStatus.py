import discord
from discord import ui
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.Database.ManageOnlyDatabase import ManageOnlyDatabase
from src.components.LayoutView.LayoutError import LayoutError

class RefreshDatabaseStatus(ui.Button):
    def __init__(self, db_id: str):
        super().__init__(
            label="Atualizar Dados",
            style=discord.ButtonStyle.secondary,
            emoji=emoji.restart
        )
        self.db_id = db_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # STATUS REQ

        req_status = await squarecloud_request.get_database_status(self.db_id)

        if isinstance(req_status, SquareErrorModel):
            code = req_status.code
            msg = code if code else "Erro ao buscar status do database."

            return await interaction.followup.send(view=LayoutError(msg))

        # INFO REQ

        req_info = await squarecloud_request.get_me()

        if isinstance(req_info, SquareErrorModel):
            code = req_info.code
            msg = code if code else "Erro ao buscar informações do database."

            return await interaction.followup.send(view=LayoutError(msg))

        databases = req_info.get("databases", [])

        database_info = next(
            (db for db in databases if db.get("id") == self.db_id),
            None
        )

        if not database_info:
            return await interaction.followup.send(
                view=LayoutError("DATABASE_NOT_FOUND"),
                ephemeral=True
            )
            
        database_status = req_status

        await interaction.edit_original_response(
            view=ManageOnlyDatabase(database_info, database_status)
        )