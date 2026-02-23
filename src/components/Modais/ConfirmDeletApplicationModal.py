import discord
from base import emoji, squarecloud_request
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.ListApplications import ListApplications
from base.request.models import SquareErrorModel

class ConfirmDeletApplicationModal(discord.ui.Modal):
    def __init__(self, application_id: str):
        super().__init__(timeout=None, title="Confirmação de Exclusão")
        
        self.confirm = discord.ui.TextDisplay(
            content=f" {emoji.delete} Tem certeza que deseja esta aplicação? Está ação é **IRREVERSÍVEL**. Ao ser deletado, você nunca mais poderá recuperar esta aplicação.",
        )
        
        self.add_item(self.confirm)
        self.application_id = application_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        result = await squarecloud_request.delete_app(self.application_id)

        if isinstance(result, SquareErrorModel):
            code = result.code
            msg = code if code else "Erro ao deletar aplicação."
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

        applications = data["applications"]

        return await interaction.edit_original_response(
            view=ListApplications(applications)
        )
