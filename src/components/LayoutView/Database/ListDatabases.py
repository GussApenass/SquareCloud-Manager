import discord
from typing import List
from base import emoji
from src.components.LayoutView.SelectTypeApplication import SelectTypeApplication

ITEMS_PER_PAGE = 5

def chunk_databases(apps: list):
    return [
        apps[i:i + ITEMS_PER_PAGE]
        for i in range(0, len(apps), ITEMS_PER_PAGE)
    ]

class ListDatabases(discord.ui.LayoutView):
    def __init__(self, databases: List[dict]):
        super().__init__(timeout=None)

        self.databases = databases

        self.pages = chunk_databases(databases) if databases else [[]]
        self.page = 0
        self.max_page = max(0, len(self.pages) - 1)

        self.render()

    def render(self):
        self.clear_items()

        from src.components.Buttons.Database.ManageOnlyDatabaseButton import ManageOnlyDatabaseButton
        from src.components.Buttons.Database.DatabasePaginatorButton import DatabasePaginationButton
        from src.components.Buttons.Database.UploadDatabaseButton import UploadDatabaseButton
        from src.components.Buttons.BackButton import BackButton

        apps_page = self.pages[self.page]

        sections = []

        for app in apps_page:
            name = app.get("name", "Sem nome")
            ram = app.get("ram", 0)
            db_type = app.get("type", "unknown").lower()
            cluster = app.get("cluster", "Sem cluster")

            formatted_types = {
                "mongo": f"{emoji.mongodb} MongoDB",
                "postgres": f"{emoji.postgres} PostgreSQL",
                "redis": f"{emoji.redis} Redis",
                "mysql": f"{emoji.mysql} MySQL"
            }

            type_display = formatted_types.get(db_type, f"{db_type.capitalize()}")

            text = (
                f"**{name} | {ram}MB**\n"
                f"{type_display} | Cluster: {cluster}"
            )

            sections.append(
                discord.ui.Section(
                    text,
                    accessory=ManageOnlyDatabaseButton(app["id"], app)
                )
            )

        self.row = discord.ui.ActionRow(
            DatabasePaginationButton(emoji.backback, "first"),
            DatabasePaginationButton(emoji.back, "prev"),
            DatabasePaginationButton(emoji.next, "next"),
            DatabasePaginationButton(emoji.nextnext, "last"),
        )

        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.edit_original_response(view=SelectTypeApplication())

        container_items = [
            discord.ui.Section(
                f"## {emoji.rocket} | Banco de Dados\n"
                f"-# No total, são {len(self.databases)} Bancos de dados!",
                accessory=UploadDatabaseButton()
            ),
            discord.ui.Separator()
        ]

        if sections:
            container_items.extend(sections)
        else:
            container_items.append(discord.ui.TextDisplay("*Nenhum banco de dados encontrado.*"))

        container_items.extend([
            discord.ui.Separator(spacing=discord.SeparatorSpacing.large),
            self.row,
            discord.ui.ActionRow(BackButton(return_func))
        ])

        container = discord.ui.Container(
            *container_items,
            accent_colour=discord.Colour(4519199),
        )

        self.add_item(container)
        self.update_buttons()

    def update_buttons(self):
        first, prev, next_, last = self.row.children

        first.disabled = self.page == 0
        prev.disabled = self.page == 0
        next_.disabled = self.page == self.max_page
        last.disabled = self.page == self.max_page