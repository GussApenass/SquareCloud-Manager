import json
import asyncio
import aiohttp
import base64
from pathlib import Path
from base import logger

BASE_DIR = Path(__file__).parent
JSON_PATH = BASE_DIR / "emojis.json"
FILES_DIR = BASE_DIR / "files"
EMOJI_PY = BASE_DIR / "emoji.py"


# ================= MANAGER =================

class EmojiManager:
    def __init__(self):
        self.refresh()

    def refresh(self):
        if not JSON_PATH.exists():
            return

        with open(JSON_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for name, info in data.items():
                    if isinstance(info, dict):
                        emoji_id = info.get("id")
                        is_animated = info.get("animated", False)
                        prefix = "a" if is_animated else ""
                        setattr(self, name, f"<{prefix}:{name}:{emoji_id}>")
                    else:
                        setattr(self, name, f"<:{name}:{info}>")
            except Exception as e:
                logger.error(f"Erro ao carregar emojis: {e}")


emoji = EmojiManager()


# ================= AUTOGEN FILE =================

def _write_emoji_py(emoji_dict: dict):
    lines = [
        "from .emoji_manager import emoji as _emoji_runtime\n",
        "from typing import cast\n\n"
        "class EmojiTypes:\n",
    ]

    if not emoji_dict:
        lines.append("    pass\n")
    else:
        for name in emoji_dict:
            lines.append(f"    {name}: str\n")

    lines.append("\nemoji = cast(EmojiTypes, _emoji_runtime)")

    EMOJI_PY.write_text("".join(lines), encoding="utf-8")


# ================= LOAD JSON =================

def _load_json():
    if not JSON_PATH.exists():
        return {}

    try:
        return json.loads(JSON_PATH.read_text())
    except:
        return {}


# ================= SYNC =================

async def load_emojis(bot_token: str, application_id: str):
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json"
    }

    api_url = f"https://discord.com/api/v10/applications/{application_id}/emojis"

    local_files = {
        f.stem: f
        for f in FILES_DIR.iterdir()
        if f.suffix in (".png", ".jpg", ".jpeg", ".gif")
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers=headers) as r:
            data = await r.json()
            remote = data["items"] if isinstance(data, dict) else data

        remote_map = {e["name"]: {"id": e["id"], "animated": e.get("animated", False)} for e in remote}
        emoji_json = _load_json()

        for name, file in local_files.items():
            existing = remote_map.get(name)
            is_animated = file.suffix.lower() == ".gif"

            current_local_id = emoji_json.get(name, {}).get("id") if isinstance(emoji_json.get(name), dict) else emoji_json.get(name)

            if not existing or current_local_id != existing["id"]:
                if existing:
                    await session.delete(f"{api_url}/{existing['id']}", headers=headers)

                encoded = base64.b64encode(file.read_bytes()).decode()
                ext = file.suffix[1:].replace("jpg", "jpeg")

                payload = {
                    "name": name,
                    "image": f"data:image/{ext};base64,{encoded}"
                }

                async with session.post(api_url, headers=headers, json=payload) as p:
                    res = await p.json()
                    if p.status in (200, 201):
                        emoji_json[name] = {
                            "id": res["id"],
                            "animated": is_animated
                        }
                        logger.success(f"Emoji sync: {name} ({'Animado' if is_animated else 'Estático'})")
                    else:
                        logger.error(f"Falha ao subir emoji '{name}': {res}")
                        continue
            else:
                emoji_json[name] = existing

        JSON_PATH.write_text(json.dumps(emoji_json, indent=4), encoding="utf-8")
        _write_emoji_py(emoji_json)
        emoji.refresh()