from typing import Any, Dict
import discord
import time
from base.discord import Modal, TextInput, CheckBox, Label, TextInputStyle
from base import emoji, squarecloud_request
from base.request.models import SquareErrorModel
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.LayoutManageOnlyFile import LayoutManageOnlyFile

class MoveAppFile(Modal):
    def __init__(self, application_id: str, path: str, file_data: Dict[str, Any]):
        super().__init__(title="Mova o arquivo")

        self.application_id = application_id
        self.file_data = file_data
        self.path = path

        self.to = Label(
            text="O caminho para o qual o arquivo será movido",
            description="Coloque um caminho neste formato: src/commands",
            component=TextInput(
                placeholder="src/commands",
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
            view=LayoutLoading("Movendo o arquivo..."),
            ephemeral=True
        )

        to = self.to.text_value.rstrip('/')
        filename = self.file_data.get("name")

        if not to:
            return await loading_message.edit(
                view=LayoutError(f"{emoji.xred} **|** Nenhum caminho enviado.")
            )

        request = await squarecloud_request.move_app_file(self.application_id, self.path, to, filename)

        if isinstance(request, SquareErrorModel):
            code = request.code
            msg = code if code else "Erro ao mover o arquivo."
            return await loading_message.edit(view=LayoutError(msg))

        await loading_message.edit(view=LayoutInfo(f"{emoji.check} **|** Arquivo movido com sucesso!"))

        self.file_data["lastModified"] = int(time.time() * 1000)

        file_path = f"{to}/{self.file_data['name']}"

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
        
        await interaction.edit_original_response(view=LayoutManageOnlyFile(self.application_id, self.file_data, file_path))