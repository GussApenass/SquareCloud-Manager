import discord
from base import emoji

class InitialLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        from src.components.Buttons.SelectTypeEnterButton import SelectTypeEnterButton
        from src.components.Buttons.Profile.ProfileMenuButton import ProfileMenuButton

        container1 = discord.ui.Container(
            discord.ui.TextDisplay(content=f"## {emoji.SquareCloud} Square Cloud Manager"),

            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),

            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"### {emoji.application} Aplicações\n- Veja suas aplicações e gerencie elas diretamente pelo Discord."
                ),
                accessory=SelectTypeEnterButton()
            ),

            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),

            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"### {emoji.team} Área de Trabalho\n- Veja as **áreas de trabalhos** em que você faz parte, **gerencie elas**, **adicione novos membros** (*Apenas se você for o dono*) e **gerencie as aplicações**."
                ),
                accessory=discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Friendly Lion",
                    custom_id="eb7f61b01c8d4450a5f2a8599d36d395",
                ),
            ),

            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),

            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"### {emoji.img} Blob\n- Gerencie seu [Blob](), **veja os objetos**, **adicione novos objetos**, **delete objetos** e **altere os objetos**\n-# Mas afinal, o que é o **Blob**?\n-# Blob é um objeto binário (Binary Large Object) usado para armazenar dados \"crus\", como imagens, áudios ou arquivos."
                ),
                accessory=discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Colorful Swallow",
                    custom_id="7c8a778a1bf84432d01877b7677927c4",
                ),
            ),

            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),

            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"### {emoji.user} Perfil\n- Veja detalhes da sua conta na Square Cloud"
                ),
                accessory=ProfileMenuButton()
            ),

            accent_colour=discord.Colour(956923),
        )

        self.add_item(container1)