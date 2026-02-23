import os
import discord
from discord.ext import commands
from base import logger, emoji
from base.emojis.emoji_manager import load_emojis
from base.env.config import env

PASTAS = {
    "slash": "src/slash",
}

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.none()

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.loaded_extensions = []

    async def setup_hook(self):
        logger.success("☰ Variáveis de ambiente carregadas")

        logger.info("↳ Sincronizando emojis...")
        try:
            await load_emojis(env.BOT_TOKEN, env.APPLICATION_ID)
            logger.success("↳ Emojis sincronizados")
        except Exception as e:
            logger.error(f"Erro ao carregar emojis: {e}")

        logger.info("ℹ Carregando módulos do sistema:")

        stats = {}

        for tipo, pasta in PASTAS.items():
            if not os.path.exists(pasta):
                logger.error(f"Pasta não encontrada: {pasta}")
                continue

            files = [
                f for f in os.listdir(pasta)
                if f.endswith(".py") and not f.startswith("__")
            ]

            stats[tipo] = len(files)

            logger.info(f"  └ {tipo.capitalize()} Commands: {len(files)} encontrados")

            for file in files:
                ext = f"{pasta.replace('/', '.')}.{file[:-3]}"
                try:
                    await self.load_extension(ext)
                    self.loaded_extensions.append(ext)

                    icon = "{/}"
                    logger.success(f"{icon} {file[:-3]} -> Carregado com sucesso!")

                except Exception as e:
                    logger.error(f"Falha ao carregar {ext}: {e}")


        await self.tree.sync()

        total = sum(stats.values())

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.success("Square Cloud Manager • Build by GussApenass")
        logger.success(f"● {self.user or 'Bot'}")
        logger.success(f"  └ {total} comandos registrados globalmente")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def bootstrap():
    bot = MyBot()
    try:
        bot.run(env.BOT_TOKEN)
    except Exception as e:
        logger.critical(f"Erro fatal ao iniciar o bot: {e}")