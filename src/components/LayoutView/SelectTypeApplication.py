import discord
from base import emoji
from src.components.Buttons.BackButton import BackButton
from src.components.LayoutView.InitialLayout import InitialLayout

class SelectTypeApplication(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        from src.components.Buttons.AppManageButton import AppManageButton
        from src.components.Buttons.Database.DatabaseManageButton import DatabaseManageButton
    
        async def return_func(interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.edit_original_response(view=InitialLayout())
        
        container1 = discord.ui.Container(
            discord.ui.TextDisplay(content=f"## {emoji.rocket} Square Cloud Manager"),
            discord.ui.TextDisplay(content="- Selecione quais tipos de aplicações você quer gerenciar (*Banco de dados* ou *Aplicações* (*Bots, websites, entre outros*)"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"### {emoji.application} Aplicações\n- Gerencie suas **aplicações** (*Bot, websites, entre outros*)"),
                accessory=AppManageButton()
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(content=f"### {emoji.database} Database\n- Gerencie seus **banco de dados** (*MongoDB*, *Redis*, *Entre outros*)"),
                accessory=DatabaseManageButton()
            ),
            discord.ui.Separator(),
            discord.ui.ActionRow(
                BackButton(return_func)
            ),
            accent_colour=discord.Colour(51451),
        )
        self.add_item(container1)