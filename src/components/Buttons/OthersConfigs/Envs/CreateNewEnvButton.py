import discord
from base import emoji
from src.components.Modais.OthersConfigs.Envs.CreateNewEnvModal import CreateNewEnvModal

class CreateNewEnvButton(discord.ui.Button):
    def __init__(self, application_id: str):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji.create
        )
        self.application_id = application_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CreateNewEnvModal(self.application_id))