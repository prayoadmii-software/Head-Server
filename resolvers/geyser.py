import requests
import tempfile
import os
import uuid

from pathlib import Path
from prayoadmii_lib import console
from prayoadmii_lib.configlib import tomlcfg

async def resolve_bedrock_skin(gamertag: str) -> tuple[bool, Path | None, str]:
    CONFIG = tomlcfg.load("config.toml")
    TMP_DIR = CONFIG.get_config("cache.tmp_folder_name", "head_server")
    USR_AGENT = CONFIG.get_config("request.user_agent")
    TIMEOUT = CONFIG.get_config("request.api_timeouts", 15)
    HEADERS = {"User-Agent": str(USR_AGENT)}

    gamertag = gamertag.strip()

    if not gamertag:
        return False, None, "No Gamertag Provided!"

    console.log(f"Getting Bedrock Skin For {str(gamertag)}")


    try:
        console.log(f"[NOW PENDING] Get XUID Of {str(gamertag)}")

        data = requests.get(
            url=f"https://api.geysermc.org/v2/xbox/xuid/{str(gamertag)}",
            timeout=int(TIMEOUT),
            headers=HEADERS
        )

        data.raise_for_status()

        geyser_xuid_data = data.json()
    except Exception as e:
        console.error(f"There Are An Error While Getting XUID Of {str(gamertag)} As {str(e)}!")

        return False, None, f"There Are An Error While Getting XUID Of {str(gamertag)} As {str(e)}!"

    console.log(f"[LOADING] Get XUID Of {str(gamertag)}")

    geyser_xuid = geyser_xuid_data.get("xuid", None)

    if geyser_xuid is None:
        console.error("There's No Valid XUID Returned From API Request!")

        return False, None, "There's No Valid XUID Returned From API Request!"

    console.log(f"[DONE] Get XUID Of {str(gamertag)}")


    try:
        console.log(f"[NOW PENDING] Get Texture ID Of {str(geyser_xuid)}")

        data = requests.get(
            url=f"https://api.geysermc.org/v2/skin/{str(geyser_xuid)}",
            timeout=int(TIMEOUT),
            headers=HEADERS
        )

        data.raise_for_status()

        geyser_skin_data = data.json()
    except Exception as e:
        console.error(f"There Are An Error While Getting Skin Data Of {str(geyser_xuid)} As {str(e)}!")

        return False, None, f"There Are An Error While Getting Skin Data Of {str(geyser_xuid)} As {str(e)}!"

    console.log(f"[LOADING] Get Texture ID Of {str(geyser_xuid)}")

    geyser_texture_id = geyser_skin_data.get("texture_id", None)

    if geyser_texture_id is None:
        console.error("There's No Valid Texture ID Returned From API Request!")
        
        return False, None, "There's No Valid Texture ID Returned From API Request!"

    console.log(f"[DONE] Get Texture ID Of {str(geyser_xuid)}")


    DOWNLOAD_PATH = Path(tempfile.gettempdir()) / str(TMP_DIR) / "module_cache" / f"{str(uuid.uuid4())}.png"
    DOWNLOAD_URL = f"http://textures.minecraft.net/texture/{str(geyser_texture_id)}"

    DOWNLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)