import discord
from base import emoji, squarecloud_request
from src.components.LayoutView.Database.ListDatabases import ListDatabases
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.ListApplications import ListApplications
from base.request.models import SquareErrorModel

class ConfirmDeletDatabaseModal(discord.ui.Modal):
    def __init__(self, database_id: str):
        super().__init__(timeout=None, title="Confirmação de Exclusão")

        self.confirm = discord.ui.TextDisplay(
            content=f" {emoji.delete} Tem certeza que deseja este banco de dados? Está ação é **IRREVERSÍVEL**. Ao ser deletado, você nunca mais poderá recuperar os dados deste banco de dados. Isso é uma ação bem séria...",
        )

        self.add_item(self.confirm)
        
        self.database_id = database_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        result = await squarecloud_request.delete_db(self.database_id)

        if isinstance(result, SquareErrorModel):
            code = result.code
            msg = code if code else "Erro ao deletar database."
            return await interaction.followup.send(
                view=LayoutError(msg),
                ephemeral=True
            )

        data = await squarecloud_request.get_me()

        if isinstance(data, SquareErrorModel):
            code = data.code if data.code else "Erro ao buscar aplicações."

            return await interaction.edit_original_response(
                view=LayoutError(code)
            )

        databases = data.get("databases", [])

        return await interaction.edit_original_response(
            view=ListDatabases(databases)
        )
