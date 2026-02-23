import discord
from typing import List
from base import emoji
from src.components.LayoutView.OthersConfiguration import OthersConfiguration

ITEMS_PER_PAGE = 5

def chunk_files(files: list):
    return [
        files[i:i + ITEMS_PER_PAGE]
        for i in range(0, len(files), ITEMS_PER_PAGE)
    ]

class LayoutManagerApplicationsFiles(discord.ui.LayoutView):
    def __init__(self, application_id: str, files: List[dict], path: str):
        super().__init__(timeout=None)

        self.files = files
        self.application_id = application_id
        self.path = path

        self.pages = chunk_files(files)
        self.page = 0
        self.max_page = len(self.pages) - 1

        self.render()

    def render(self):
        self.clear_items()

        from src.components.Buttons.ManageOnlyApplicationsFile import ManageOnlyApplicationFile
        from src.components.Buttons.ApplicationPaginatorFiles import ApplicationPaginatorFiles
        from src.components.Buttons.SearchApplicationFile import SearchApplicationFile
        from src.components.Buttons.CreateNewArchiveButton import CreateNewArchiveButton
        from src.components.Buttons.BackButton import BackButton

        files_page = self.pages[self.page]

        sections = []

        for file_data in files_page:
            name = file_data.get("name", "Desconhecido")
            f_type = file_data.get("type", "file")

            size_raw = file_data.get("size", 0)

            last_mod_ms = file_data.get("lastModified", 0)
            if last_mod_ms and last_mod_ms > 0:
                timestamp = int(last_mod_ms / 1000)
                time_text = f"-# {emoji.date} Modificado: <t:{timestamp}:F> <t:{timestamp}:R>\n"
            else:
                time_text = None

            icon = emoji.files if f_type == "directory" else emoji.file

            display_type = "Arquivo" if f_type == "file" else "Pasta"

            size_text = ""
            if f_type == "file":
                n = 0
                units = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB'}
                size_calc = float(size_raw)

                while size_calc >= 1024 and n < 3:
                    size_calc /= 1024
                    n += 1

                formatted_size = f"{size_calc:.2f}" if n > 0 else f"{int(size_calc)}"
                size_text = f"`{formatted_size}{units[n]}`"

            size_line = f"-# {emoji.diskcard} Tamanho: {size_text}\n" if f_type == "file" else None
            tipo_line = f"-# {emoji.next} Tipo: `{display_type}`\n" if f_type == "file" else None

            text = (
                f"{icon} **{name}**\n"
            )

            if size_line is not None:
                text += size_line

            if tipo_line is not None:
                text += tipo_line

            if time_text is not None:
                text += time_text

            path_formatado = f"{self.path.rstrip('/')}/{name}"

            sections.append(
                discord.ui.Section(
                    text,
                    accessory=ManageOnlyApplicationFile(self.application_id, file_data, f_type, path_formatado)
                )
            )

        self.row = discord.ui.ActionRow(
            ApplicationPaginatorFiles(emoji.backback, "first"),
            ApplicationPaginatorFiles(emoji.back, "prev"),
            discord.ui.Button(
                label=f"{self.page + 1}/{self.max_page + 1}",
                style=discord.ButtonStyle.gray,
                disabled=True
            ),
            ApplicationPaginatorFiles(emoji.next, "next"),
            ApplicationPaginatorFiles(emoji.nextnext, "last"),
        )

        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.edit_original_response(view=OthersConfiguration(self.application_id))

        container = discord.ui.Container(
            discord.ui.ActionRow(SearchApplicationFile(self.application_id, self.path)),
            discord.ui.Separator(),
            discord.ui.Section(
                f"## {emoji.files} | Arquivos no path \n"
                f"-# No total, são `{len(self.files)}` (Total de {self.max_page + 1} páginas) arquivos no `{self.path}`!",
                accessory=CreateNewArchiveButton(self.application_id)
            ),
            discord.ui.Separator(),
            *sections,
            discord.ui.Separator(spacing=discord.SeparatorSpacing.large),
            self.row,
            discord.ui.ActionRow(BackButton(return_func)),
            accent_colour=discord.Colour(4519199),
        )

        self.add_item(container)
        self.update_buttons()

    def update_buttons(self):
        first, prev, page_btn, next_, last = self.row.children

        first.disabled = self.page == 0
        prev.disabled = self.page == 0
        next_.disabled = self.page == self.max_page
        last.disabled = self.page == self.max_page