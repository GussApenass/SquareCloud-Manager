import discord
from base.discord import Modal, TextDisplay, CheckBox, Label
from base import emoji, squarecloud_request
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.LayoutManagerApplicationsFiles import LayoutManagerApplicationsFiles
from base.request.models import SquareErrorModel

class ConfirmDeleteFileModal(Modal):
    def __init__(self, application_id: str, path: str):
        super().__init__(timeout=None, title="Confirmação de Exclusão")

        self.confirm = TextDisplay(
            content=f" {emoji.delete} Tem certeza que deseja deletar este arquivo? Está ação é **IRREVERSÍVEL**. Ao ser deletado, você nunca mais poderá recuperar este arquivo. (*Apenas caso sua aplicação esteja no Github, Gitlab ou salva em algum lugar!*)",
        )

        self.restart_app = Label(
            text="Deseja Reiniciar a aplicação?",
            description="Selecione esta caixa caso queira que a aplicação seja reiniciada.",
            component=CheckBox(
                default=False
            )
        )
        
        self.application_id = application_id
        self.path = path

    async def on_submit(self, interaction: discord.Interaction):
        await self._parse_custom_interaction(interaction)
        await interaction.response.defer()

        loading_message = await interaction.followup.send(view=LayoutLoading("Deletando arquivo..."), ephemeral=True)

        result = await squarecloud_request.delete_app_file(self.application_id, self.path)

        if isinstance(result, SquareErrorModel):
            code = result.code
            msg = code if code else "Erro ao deletar arquivo."
            return await loading_message.edit(view=LayoutError(msg))

        path = "/"

        result_path = await squarecloud_request.get_app_files(self.application_id, path)

        if isinstance(result_path, SquareErrorModel):
            error_msg = str(result_path.code) if result_path.code else "Erro ao buscar arquivos."
            return await loading_message.edit(view=LayoutError(error_msg))

        files_list = result_path

        view=LayoutManagerApplicationsFiles(self.application_id, files_list, path)

        # RESTART APP

        if self.restart_app.checked:
            loading_restart_message = await interaction.followup.send(
                view=LayoutLoading("Reiniciando aplicação..."),
                ephemeral=True
            )

            restart = await squarecloud_request.restart_app(self.application_id)

            if isinstance(restart, SquareErrorModel):
                code = restart.code
                msg = code if code else "Erro ao reiniciar aplicação."
                return await loading_restart_message.edit(view=LayoutError(msg))

            await loading_restart_message.edit(
                view=LayoutInfo(f"{emoji.check} Aplicação reiniciada com sucesso!")
            )

        await interaction.edit_original_response(
            view=view
        )
        await loading_message.edit(view=LayoutInfo(f"{emoji.check} **|** Arquivo deletado com sucesso!"))
