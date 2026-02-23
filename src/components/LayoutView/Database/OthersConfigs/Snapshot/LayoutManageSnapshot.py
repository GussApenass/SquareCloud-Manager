import discord
from typing import List, Any
from base import emoji
from urllib.parse import parse_qs
from src.components.LayoutView.Database.OthersConfigs.OthersConfigsLayout import OthersConfigsLayout
from datetime import datetime

ITEMS_PER_PAGE = 5

def format_size(bytes_size: float) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"

def chunk_snapshots(snapshots: List[Any]) -> List[List[Any]]:
    return [
        snapshots[i : i + ITEMS_PER_PAGE]
        for i in range(0, len(snapshots), ITEMS_PER_PAGE)
    ]

def extract_version_id(key_string: str) -> str:
    query_params = parse_qs(key_string)
    version_list = query_params.get("versionId", [])
    return version_list[0] if version_list else key_string

class LayoutManagerSnapshot(discord.ui.LayoutView):
    def __init__(self, database_id: str, account_id, snapshots: List[dict]):
        super().__init__(timeout=None)

        self.database_id = database_id
        self.account_id = account_id
        self.raw_snapshots = snapshots

        self.pages = chunk_snapshots(snapshots)
        self.page = 0
        self.max_page = max(0, len(self.pages) - 1)

        self.render()

    def render(self):
        self.clear_items()

        from src.components.Buttons.BackButton import BackButton
        from src.components.Buttons.Database.OthersConfigs.Snapshot.DatabasePaginatorSnapshot import DatabasePaginatorSnapshot
        from src.components.Buttons.Database.OthersConfigs.Snapshot.RestaurarDbsSnapshot import RestaurarDbsSnapshot

        current_page_snapshots = self.pages[self.page] if self.pages else []

        sections = []

        for snap in current_page_snapshots:
            name = snap.get('name')
            key = snap.get('key')
            size = snap.get('size', 0)
            modified = snap.get('modified')

            download_url = f"https://snapshots.squarecloud.app/databases/{self.account_id}/{name}.zip?{key}"
            version_id = extract_version_id(key)
            size_readable = format_size(size)

            dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))

            unix_timestamp = int(dt.timestamp())

            discord_timestamp = f"<t:{unix_timestamp}:F> (<t:{unix_timestamp}:R>)"

            text = (
                f"{emoji.snapshot} **Snapshot: `{name[:8]}...`**\n"
                f"-# {emoji.clock} Modificado: {discord_timestamp}\n"
                f"-# {emoji.files} Tamanho: `{size_readable}`\n"
                f"-# {emoji.link} [Clique para baixar o ZIP]({download_url})"
            )

            sections.append(
                discord.ui.Section(
                    text,
                    accessory=RestaurarDbsSnapshot(self.database_id, self.account_id, name, version_id) 
                )
            )

        paginator_row = discord.ui.ActionRow(
            DatabasePaginatorSnapshot(emoji.backback, "first"),
            DatabasePaginatorSnapshot(emoji.back, "prev"),
            discord.ui.Button(
                label=f"{self.page + 1}/{self.max_page + 1}",
                style=discord.ButtonStyle.gray,
                disabled=True
            ),
            DatabasePaginatorSnapshot(emoji.next, "next"),
            DatabasePaginatorSnapshot(emoji.nextnext, "last"),
        )

        self.update_buttons(paginator_row)

        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.edit_original_response(view=OthersConfigsLayout(self.database_id))

        container = discord.ui.Container(
            discord.ui.TextDisplay(
                f"## {emoji.snapshot} | Snapshots de seu Database\n"
                f"-# Backups automáticos e manuais. Total: `{len(self.raw_snapshots)}`",
            ),
            discord.ui.Separator(),
            *sections if sections else [discord.ui.TextDisplay("Nenhum snapshot disponível.")],
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