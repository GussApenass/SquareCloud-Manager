import discord
from typing import Any, Dict, List
from base import emoji
from src.components.LayoutView.OthersConfiguration import OthersConfiguration

ITEMS_PER_PAGE = 5

def chunk_envs(envs: Dict[str, str]) -> List[List[Dict[str, str]]]:
    env_list = [{"key": k, "value": v} for k, v in envs.items()]

    return [
        env_list[i : i + ITEMS_PER_PAGE]
        for i in range(0, len(env_list), ITEMS_PER_PAGE)
    ]

class LayoutManagerApplicationsEnvs(discord.ui.LayoutView):
    def __init__(self, application_id: str, envs: Dict[str, str]):
        super().__init__(timeout=None)

        self.application_id = application_id
        self.raw_envs = envs

        self.pages = chunk_envs(envs)
        self.page = 0
        self.max_page = max(0, len(self.pages) - 1)

        self.render()

    def render(self):
        self.clear_items()

        from src.components.Buttons.OthersConfigs.Envs.ManageOnlyEnv import ManageOnlyEnv
        from src.components.Buttons.OthersConfigs.Envs.ApplicationPaginatorEnv import ApplicationPaginatorEnv
        from src.components.Buttons.BackButton import BackButton
        from src.components.Buttons.OthersConfigs.Envs.CreateNewEnvButton import CreateNewEnvButton

        current_page_envs = self.pages[self.page] if self.pages else []

        sections = []

        for env_data in current_page_envs:
            key = env_data["key"]
            value = env_data["value"]

            text = (
                f"{emoji.security} **{key}**\n"
                f"-# {emoji.next} Valor: ||`{value}`||"
            )

            sections.append(
                discord.ui.Section(
                    text,
                    accessory=ManageOnlyEnv(self.application_id, key, value)
                )
            )

        paginator_row = discord.ui.ActionRow(
            ApplicationPaginatorEnv(emoji.backback, "first"),
            ApplicationPaginatorEnv(emoji.back, "prev"),
            discord.ui.Button(
                label=f"{self.page + 1}/{self.max_page + 1}",
                style=discord.ButtonStyle.gray,
                disabled=True
            ),
            ApplicationPaginatorEnv(emoji.next, "next"),
            ApplicationPaginatorEnv(emoji.nextnext, "last"),
        )

        self.update_buttons(paginator_row)

        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.edit_original_response(view=OthersConfiguration(self.application_id))

        container = discord.ui.Container(
            discord.ui.Section(
                f"## {emoji.security} | Variáveis de Ambiente\n"
                f"-# Gerencie as secrets da sua aplicação. Total: `{len(self.raw_envs)}`",
                accessory=CreateNewEnvButton(self.application_id)
            ),
            discord.ui.Separator(),
            *sections if sections else [discord.ui.TextDisplay("Nenhuma variável encontrada.")],
            discord.ui.Separator(spacing=discord.SeparatorSpacing.large),
            paginator_row,
            discord.ui.ActionRow(BackButton(return_func)),
            accent_colour=discord.Colour(4519199),
        )

        self.add_item(container)

    def update_buttons(self, row: discord.ui.ActionRow):
        if not row or not row.children: 
            return

        first = row.children[0]
        prev = row.children[1]
        page_btn = row.children[2]
        next_btn = row.children[3]
        last = row.children[4]

        first.disabled = self.page == 0
        prev.disabled = self.page == 0
        next_btn.disabled = self.page >= self.max_page
        last.disabled = self.page >= self.max_page

        page_btn.label = f"{self.page + 1}/{self.max_page + 1}"