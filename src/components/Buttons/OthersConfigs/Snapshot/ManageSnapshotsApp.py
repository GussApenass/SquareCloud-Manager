import discord
from base import emoji, squarecloud_request
from src.components.LayoutView.LayoutError import LayoutError
from src.components.LayoutView.LayoutLoading import LayoutLoading
from src.components.LayoutView.LayoutInfo import LayoutInfo
from src.components.LayoutView.OthersConfigs.Snapshot.LayoutManageSnapshot import LayoutManagerSnapshot
from base.request.models import SquareErrorModel

class ManageSnapshotsApp(discord.ui.Button):
    def __init__(self, app_id: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.menu2
        )
        self.app_id = app_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        msg = await interaction.followup.send(
            view=LayoutLoading("Buscando snapshots...")
        )
        
        req = await squarecloud_request.get_app_snapshots(self.app_id)

        if isinstance(req, SquareErrorModel):
            code = req.code
            msg = code if code else "Erro ao buscar snapshots."
            return await msg.edit(
                view=LayoutError(msg),
                ephemeral=True
            )

        snapshot_list = req

        req_me = await squarecloud_request.get_me()

        if isinstance(req_me, SquareErrorModel):
            code = req_me.code
            msg = code if code else "Erro ao buscar informações da conta."
            return await msg.edit(
                view=LayoutError(msg),
                ephemeral=True
            )

        user_data = req_me.get("user", {})
        user_id = user_data.get("id")
        
        await msg.edit(
            view=LayoutInfo(f"{emoji.check} **|** Snapshots encontradas com sucesso!")
        )

        await msg.delete()

        await interaction.edit_original_response(
            view=LayoutManagerSnapshot(self.app_id, user_id, snapshot_list)
        )