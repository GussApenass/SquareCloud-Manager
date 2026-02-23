import discord
import time
from base.discord import Modal, TextInput, FileUpload, Label, TextInputStyle, TextDisplay, CheckBox
from base import squarecloud_request, emoji
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutManagerApplicationsFiles import LayoutManagerApplicationsFiles

class CreateNewArchive(Modal):
    def __init__(self, application_id: str):
        super().__init__(timeout=None, title="Criar Novo Arquivo")

        self.aviso = TextDisplay(
            content="-# Observação: NÃO **UTILIZE O CAMINHO ASSIM:** `src/commands`, utilize assim: `src/commands/texto.py`. Caso utilize da forma incorreta, um erro será enviado."
        )

        self.path_selected = Label(
            text="Digite o caminho do arquivo.",
            description="Digite o caminho onde o novo arquivo será criado.",
            component=TextInput(
                style=TextInputStyle.short,
                placeholder="src/commands/novo_comando.py",
                required=True
            )
        )

        self.arquivo_upload = Label(
            text="Faça o upload do novo arquivo.",
            description="Este será o conteudo do arquivo que será criado.",
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

    async def on_submit(self, interaction: discord.Interaction):
        await self._parse_custom_interaction(interaction)
        
        await interaction.response.defer(ephemeral=True)

        full_path = self.path_selected.text_value
        
        if not full_path:
            return await interaction.followup.send(
                view=LayoutError("Caminho inválido ou vazio."), ephemeral=True
            )

        if "/" in full_path:
            directory_path, file_name = full_path.rsplit("/", 1)
        else:
            directory_path, file_name = "/", full_path

        result_get = await squarecloud_request.get_app_files(self.application_id, directory_path)

        if isinstance(result_get, SquareErrorModel):
            return await interaction.followup.send(view=LayoutError(str(result_get.code)), ephemeral=True)

        if any(f.get("name") == file_name for f in result_get):
            return await interaction.followup.send(
                view=LayoutError("Ops... Parece que já existe um arquivo no mesmo lugar, com o mesmo nome!"),
                ephemeral=True
            )

        try:
            attachment = self.arquivo_upload.values[0]
            file_bytes = await attachment.read()
            file_content = file_bytes.decode('utf-8')
        except Exception as e:
            return await interaction.followup.send(view=LayoutError(f"Erro ao ler arquivo: {e}"), ephemeral=True)

        result_put = await squarecloud_request.create_or_edit_app_file(self.application_id, full_path, file_content)

        if isinstance(result_put, SquareErrorModel):
            code = result_put.code
            msg = code if code else "Erro ao criar arquivo."
            return await interaction.followup.send(view=LayoutError(msg), ephemeral=True)

        current_files_dict = [dict(f) for f in result_get]
        current_files_dict.append({
            "type": "file",
            "name": file_name,
            "size": len(file_bytes),
            "lastModified": int(time.time() * 1000)
        })

        view = LayoutManagerApplicationsFiles(
            self.application_id, 
            current_files_dict, 
            directory_path
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