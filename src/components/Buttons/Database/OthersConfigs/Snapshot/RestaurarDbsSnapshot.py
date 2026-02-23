import discord
from base import emoji
from src.components.Modais.Database.OthersConfigs.Snapshot.RestaurarDbSnapshotModal import RestaurarDbSnapshotModal

ITEMS_PER_PAGE = 5

class RestaurarDbsSnapshot(discord.ui.Button):
    def __init__(self, app_id: str, account_id: int, snapshot_id: str, version_id: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.restore
        )
        self.app_id = app_id
        self.snapshot_id = snapshot_id
        self.version_id = version_id
        self.account_id = account_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RestaurarDbSnapshotModal(self.app_id, self.account_id, self.snapshot_id, self.version_id))