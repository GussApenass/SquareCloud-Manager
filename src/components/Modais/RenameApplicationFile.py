from typing import Any, Dict
import discord
import os
from base import emoji, squarecloud_request
from base.discord import Modal, TextInput, Label, CheckBox, TextInputStyle
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.LayoutManageOnlyFile import LayoutManageOnlyFile

class RenameAppFile(Modal):
    def __init__(self, application_id: str, path: str, file_data: Dict[str, Any]):
        super().__init__(title="Mova o arquivo")

        self.application_id = application_id
        self.file_data = file_data
        self.path = path

        filename_atual = file_data.get("name")
        
        self.new_filename = Label(
            text="Nome do arquivo",
            description="Digite o novo nome do arquivo, exemplo: main.py",
            component=TextInput(
                default=filename_atual,
                placeholder="main.py",
                style=TextInputStyle.short,
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

    async def on_submit(self, interaction: discord.Interaction):
        await self._parse_custom_interaction(interaction)
        await interaction.response.defer(ephemeral=True)

        loading_message = await interaction.followup.send(
            view=LayoutLoading("Renomeando o arquivo..."),
            ephemeral=True
        )

        new_filename = self.new_filename.text_value.strip('/')
        old_filename = self.file_data.get("name")

        if not new_filename:
            return await loading_message.edit(
                view=LayoutError(f"{emoji.xred} **|** Nenhum nome enviado.")
            )

        parent_dir = os.path.dirname(self.path)

        request = await squarecloud_request.move_app_file(
            self.application_id, 
            self.path, 
            parent_dir, 
            new_filename
        )

        if isinstance(request, SquareErrorModel):
            msg = request.code or "Erro ao renomear o arquivo."
            return await loading_message.edit(view=LayoutError(msg))

        self.file_data["name"] = new_filename

        new_file_path = f"{parent_dir.rstrip('/')}/{new_filename.lstrip('/')}"

        await loading_message.edit(view=LayoutInfo(f"{emoji.check} **|** Arquivo renomeado com sucesso!"))

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
            view=LayoutManageOnlyFile(self.application_id, self.file_data, new_file_path)
        )