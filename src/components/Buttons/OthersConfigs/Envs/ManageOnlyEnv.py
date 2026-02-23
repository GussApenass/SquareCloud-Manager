import discord
from discord import ui
from typing import Dict, Any
from base import emoji
from src.components.LayoutView.OthersConfigs.Envs.LayoutManageOnlyEnv import LayoutManageOnlyEnv

class ManageOnlyEnv(ui.Button):
    def __init__(self, application_id: str, chave: str, valor: str):
        self.application_id = application_id
        self.chave = chave
        self.valor = valor

        super().__init__(
            emoji=emoji.menu2,
            style=discord.ButtonStyle.secondary
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await interaction.edit_original_response(view=LayoutManageOnlyEnv(self.application_id, self.chave, self.valor))