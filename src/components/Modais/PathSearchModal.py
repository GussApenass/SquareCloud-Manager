import discord
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutManagerApplicationsFiles import LayoutManagerApplicationsFiles

class PathSearchModal(discord.ui.Modal):
    def __init__(self, application_id: str, path_atual: str = None):
        super().__init__(timeout=None, title="Buscar Pasta")

        self.confirm = discord.ui.Label(
            text="Digite o caminho da pasta.",
            description="Digite o caminho da pasta que deseja buscar os arquivos.",
            component=discord.ui.TextInput(
                style=discord.TextStyle.short,
                placeholder="src/commands",
                default=path_atual if path_atual else "/",
                required=True
            )
        )

        self.add_item(self.confirm)
        self.application_id = application_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        path = self.confirm.component.value

        result = await squarecloud_request.get_app_files(self.application_id, path)

        if isinstance(result, SquareErrorModel):
            error_msg = str(result.code) if result.code else "Erro ao buscar arquivos."
            
            return await interaction.followup.send(view=LayoutError(error_msg), ephemeral=True)

        view=LayoutManagerApplicationsFiles(self.application_id, result, path)

        await interaction.edit_original_response(
            view=view
        )
