import discord
from base import emoji

class LayoutSnapshotDownload(discord.ui.LayoutView):
    def __init__(self, url: str, filename: str | None = None):
        super().__init__(timeout=None)

        components = [
            discord.ui.TextDisplay(
                content=f"## {emoji.download} | Snapshot de seu Database"
            ),
            discord.ui.TextDisplay(
                content="- A **Snapshot** de seu database foi realizado com sucesso!\n"
                        "-# Siga o anexo abaixo (*Caso o arquivo seja muito grande, não será possível anexar, então, utilize o botão para ser redirecionado ao download*)"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        ]

        if filename:
            components.append(
                discord.ui.File(
                    media=f"attachment://{filename}"
                )
            )

        components.append(
            discord.ui.ActionRow(
                discord.ui.Button(
                    url=url,
                    emoji=emoji.download,
                    style=discord.ButtonStyle.link,
                    label="Fazer download via Web",
                ),
            )
        )

        container = discord.ui.Container(
            *components,
            accent_colour=discord.Colour(291319),
        )

        self.add_item(container)
