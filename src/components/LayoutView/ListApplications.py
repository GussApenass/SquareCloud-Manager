import discord
from typing import List
from base import emoji
from src.components.LayoutView.SelectTypeApplication import SelectTypeApplication

ITEMS_PER_PAGE = 5

def chunk_applications(apps: list):
    return [
        apps[i:i + ITEMS_PER_PAGE]
        for i in range(0, len(apps), ITEMS_PER_PAGE)
    ]

class ListApplications(discord.ui.LayoutView):
    def __init__(self, applications: List[dict]):
        super().__init__(timeout=None)

        self.applications = applications

        self.pages = chunk_applications(applications)
        self.page = 0
        self.max_page = len(self.pages) - 1

        self.render()

    def render(self):
        self.clear_items()

        from src.components.Buttons.ManageOnlyApplicationsButton import ManageOnlyApplicationButton
        from src.components.Buttons.ApplicationPaginatorButton import ApplicationPaginationButton
        from src.components.Buttons.UploadApplicationButton import UploadApplicationButton
        from src.components.Buttons.BackButton import BackButton

        apps_page = self.pages[self.page]

        sections = []

        for app in apps_page:

            name = app["name"]
            ram = app.get("ram", 0)
            desc = app.get("desc") or "Nenhuma descrição"

            desc = desc[:47] + "..." if len(desc) > 47 else desc

            text = (
                f"**{name} | {ram}mb**\n"
                f"{desc}"
            )

            sections.append(
                discord.ui.Section(
                    text,
                    accessory=ManageOnlyApplicationButton(app["id"])
                )
            )

        self.row = discord.ui.ActionRow(
            ApplicationPaginationButton(emoji.backback, "first"),
            ApplicationPaginationButton(emoji.back, "prev"),
            ApplicationPaginationButton(emoji.next, "next"),
            ApplicationPaginationButton(emoji.nextnext, "last"),
        )

        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.edit_original_response(view=SelectTypeApplication())

        container = discord.ui.Container(
            discord.ui.Section(
                f"## {emoji.rocket} | Aplicações\n"
                f"-# No total, são {len(self.applications)} aplicações!",
                accessory=UploadApplicationButton()
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
        first, prev, next_, last = self.row.children

        first.disabled = self.page == 0
        prev.disabled = self.page == 0
        next_.disabled = self.page == self.max_page
        last.disabled = self.page == self.max_page