import discord
from discord import ui
from typing import Dict, Any
from base import emoji, squarecloud_request
from src.components.Modais.OthersConfigs.Envs.EditEnvModal import EditEnvModal

class EditEnvButton(ui.Button):
    def __init__(self, application_id: str, chave: str, valor: str):
        self.application_id = application_id
        self.chave = chave
        self.valor = valor

        super().__init__(
            emoji=emoji.pencil,
            style=discord.ButtonStyle.secondary
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditEnvModal(self.application_id, self.chave, self.valor))