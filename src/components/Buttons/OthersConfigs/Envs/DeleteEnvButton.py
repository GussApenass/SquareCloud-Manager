import discord
from discord import ui
from typing import Dict, Any
from base import emoji
from src.components.Modais.OthersConfigs.Envs.ConfirmDeleteEnv import ConfirmDeleteEnv

class DeleteEnvButton(ui.Button):
    def __init__(self, application_id: str, chave: str):
        self.application_id = application_id
        self.chave = chave

        super().__init__(
            emoji=emoji.delete,
            style=discord.ButtonStyle.danger
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ConfirmDeleteEnv(self.application_id, self.chave))