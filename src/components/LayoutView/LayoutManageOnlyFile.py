import discord
from base import emoji, squarecloud_request
from typing import Optional
from src.components.Buttons.BackButton import BackButton
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutManagerApplicationsFiles import LayoutManagerApplicationsFiles
from base.request.models import SquareErrorModel

class LayoutManageOnlyFile(discord.ui.LayoutView):
    def __init__(self, application_id: str, file_data: dict, path: str):
        super().__init__(timeout=None)

        self.application_id = application_id
        self.file_data = file_data
        self.path = path

        self.name = file_data.get("name", "Desconhecido")
        self.f_type = file_data.get("type", "file")
        self.is_file = self.f_type == "file"

        self.render()

    def format_size(self) -> str:
        if not self.is_file:
            return ""

        size_calc = float(self.file_data.get("size", 0))
        units = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB'}
        n = 0

        while size_calc >= 1024 and n < 3:
            size_calc /= 1024
            n += 1

        formatted = f"{size_calc:.2f}" if n > 0 else f"{int(size_calc)}"
        return f"`{formatted}{units[n]}`"

    def get_time_text(self) -> Optional[str]:
        last_mod_ms = self.file_data.get("lastModified", 0)
        if self.is_file and last_mod_ms and last_mod_ms > 0:
            ts = int(last_mod_ms / 1000)
            return f"\n  - {emoji.date} **Modificado**: <t:{ts}:F> (<t:{ts}:R>)"
        return ""

    def render(self):
        from src.components.Buttons.EditFileContent import EditFileContentButton
        from src.components.Buttons.MoveApplicationFile import MoveApplicationFile
        from src.components.Buttons.RenameApplicationFile import RenameApplicationFile
        from src.components.Buttons.DeleteApplicationFile import DeleteApplicationFile
        from src.components.Buttons.ShowFileContent import ShowFileContent

        display_name = "Arquivo" if self.is_file else "Pasta"
        icon = emoji.file if self.is_file else emoji.files

        size_info = f"\n  - {emoji.diskcard} **Tamanho**: {self.format_size()}" if self.is_file else ""

        main_text = (
            f"- {emoji.dados_config} Dados do(a) {display_name}:\n"
            f"  - {icon} **Nome**: `{self.name}`\n"
            f"  - {emoji.next} **Tipo**: `{display_name}`"
            f"{size_info}"
            f"{self.get_time_text()}"
        )

        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer()
            
            path = "/"

            result = await squarecloud_request.get_app_files(self.application_id, path)

            if isinstance(result, SquareErrorModel):
                error_msg = str(result.code) if result.code else "Erro ao buscar arquivos."

                return await interaction.followup.send(view=LayoutError(error_msg), ephemeral=True)

            files_list = result

            view=LayoutManagerApplicationsFiles(self.application_id, files_list, path)

            await interaction.edit_original_response(
                view=view
            )

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"## {icon} | Gerenciando {display_name}"),
            discord.ui.TextDisplay(content=f"-# Path: `{self.path}`"),
            discord.ui.Separator(spacing=discord.SeparatorSpacing.small),

            discord.ui.TextDisplay(content=main_text),

            discord.ui.ActionRow(
                EditFileContentButton(self.application_id, self.path, f"{self.path}/{self.name}", self.name),
                MoveApplicationFile(self.application_id, self.path, self.file_data),
                RenameApplicationFile(self.application_id, self.path, self.file_data),
                ShowFileContent(self.application_id, self.path, self.name)
            ),
            discord.ui.ActionRow(
                DeleteApplicationFile(self.application_id, self.path)
            ),

            discord.ui.Separator(spacing=discord.SeparatorSpacing.small),

            discord.ui.ActionRow(
                BackButton(return_func)
            ),
            accent_colour=discord.Colour(587169),
        )

        self.add_item(container)