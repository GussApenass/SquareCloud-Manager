import discord
from src.components.LayoutView.Database.OthersConfigs.Snapshot.LayoutManageSnapshot import LayoutManagerSnapshot

ITEMS_PER_PAGE = 5

class DatabasePaginatorSnapshot(discord.ui.Button):
    def __init__(self, emoji: str, callback_type: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji
        )
        self.callback_type = callback_type

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        view: LayoutManagerSnapshot = self.view

        if self.callback_type == "first":
            view.page = 0
        elif self.callback_type == "prev":
            view.page = max(0, view.page - 1)
        elif self.callback_type == "next":
            view.page = min(view.max_page, view.page + 1)
        elif self.callback_type == "last":
            view.page = view.max_page

        view.render()
        await interaction.edit_original_response(view=view)