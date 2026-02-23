import discord
import time
from base.discord import Modal, TextDisplay, FileUpload, Label, CheckBox
from base import squarecloud_request, emoji
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutManageOnlyFile import LayoutManageOnlyFile
from src.components.LayoutView.LayoutInfo import LayoutInfo

class EditFileContent(Modal):
    def __init__(self, application_id: str, path: str, archive_path: str, file_name: str):
        super().__init__(timeout=None, title="Editar Arquivo")

        self.arquivo_upload = Label(
            text="Faça o upload do novo conteudo.",
            description="Ele será editado com o exato mesmo conteúdo do arquivo enviado.",
            component=FileUpload(
                min_values=1,
                max_values=1,
                required=True
            )
        )

        self.restart_app = Label(
            text="Deseja Reiniciar a aplicação?",
            description="Selecione esta caixa caso queira que a aplicação seja reiniciada.",
            component=CheckBox(
                default=False
            )
        )

        self.application_id = application_id
        self.archive_path = archive_path
        self.file_name = file_name
        self.path = path

    async def on_submit(self, interaction: discord.Interaction):
        await self._parse_custom_interaction(interaction)

        await interaction.response.defer(ephemeral=True)

        attachments = self.arquivo_upload.values
        if not attachments:
            return await interaction.followup.send(view=LayoutError("Nenhum arquivo encontrado."), ephemeral=True)

        attachment = attachments[0]
        file_bytes = await attachment.read()
        file_content = file_bytes.decode('utf-8') 

        result_edit = await squarecloud_request.create_or_edit_app_file(
            self.application_id, 
            self.path, 
            file_content
        )

        if isinstance(result_edit, SquareErrorModel):
            code = result_edit.code
            msg = str(code) if code else "Erro ao editar arquivo."
            
            return await interaction.followup.send(view=LayoutError(msg), ephemeral=True)

        result_restart = await squarecloud_request.restart_app(self.application_id)

        if isinstance(result_restart, SquareErrorModel):
            code = result_restart.code
            msg = str(code) if code else "Erro ao reiniciar aplicação."
            return await interaction.followup.send(view=LayoutError(msg), ephemeral=True)

        file_entry = {
            "type": "file",
            "name": self.file_name,
            "size": len(file_bytes),
            "lastModified": int(time.time() * 1000)
        }

        view = LayoutManageOnlyFile(self.application_id, file_entry, self.path)

        await interaction.followup.send(
            view=LayoutInfo("Arquivo editado com sucesso!"), ephemeral=True
        )

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
            
        await interaction.edit_original_response(view=view)