import tempfile
import uuid
import httpx

from pathlib import Path

from prayoadmii_lib import console
from prayoadmii_lib.configlib import tomlcfg

async def resolve(gamertag: str) -> tuple[bool, Path | None, str]:
    CONFIG = tomlcfg.load("config.toml")

    TMP_DIR = CONFIG.get_config("cache.tmp_folder_name", "head_server")
    USR_AGENT = CONFIG.get_config("request.user_agent")
    TIMEOUT = CONFIG.get_config("request.api_timeouts", 15)
    HEADERS = {
        "User-Agent": str(USR_AGENT)
    }

    gamertag = gamertag.strip()

    if not gamertag:
        return False, None, "No Gamertag Provided!"

    console.log(f"Getting Bedrock Skin For {gamertag}")

    DOWNLOAD_PATH = Path(tempfile.gettempdir()) / str(TMP_DIR) / "module_cache" / f"{uuid.uuid4()}.png"
    DOWNLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        async with httpx.AsyncClient(timeout=float(TIMEOUT), headers=HEADERS) as client:
            console.log(f"[NOW PENDING] Get XUID Of {gamertag}")

            response = await client.get(f"https://api.geysermc.org/v2/xbox/xuid/{gamertag}")

            response.raise_for_status()

            geyser_xuid_data = response.json()

            console.log(f"[LOADING] Get XUID Of {gamertag}")

            geyser_xuid = geyser_xuid_data.get("xuid")

            if geyser_xuid is None:
                console.error("There's No Valid XUID Returned From API Request!")

                return False, None, "There's No Valid XUID Returned From API Request!"

            console.log(f"[DONE] Get XUID Of {gamertag}")


            console.log(f"[NOW PENDING] Get Texture ID Of {geyser_xuid}")

            response = await client.get(f"https://api.geysermc.org/v2/skin/{geyser_xuid}")

            response.raise_for_status()

            geyser_skin_data = response.json()

            console.log(f"[LOADING] Get Texture ID Of {geyser_xuid}")

            geyser_texture_id = geyser_skin_data.get("texture_id")

            if geyser_texture_id is None:
                console.error("There's No Valid Texture ID Returned From API Request!")

                return False, None, "There's No Valid Texture ID Returned From API Request!"

            console.log(f"[DONE] Get Texture ID Of {geyser_xuid}")


            download_url = f"http://textures.minecraft.net/texture/{geyser_texture_id}"

            console.log(f"[NOW PENDING] Download Skin Texture {geyser_texture_id}")

            response = await client.get(download_url)

            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()

            if not content_type.startswith("image/"):
                console.error("Minecraft Texture Server Returned Unexpected Content-Type: {content_type}")

                return False, None, f"Minecraft Texture Server Returned Unexpected Content-Type: {content_type}"

            DOWNLOAD_PATH.write_bytes(response.content)

            console.log(f"[DONE] Download Skin Texture {geyser_texture_id}")
    except httpx.HTTPStatusError as e:
        console.error(f"HTTP Error While Resolving Bedrock Skin For {gamertag}: {e}")

        return False, None, f"HTTP Error While Resolving Bedrock Skin For {gamertag}: {e}"
    except httpx.RequestError as e:
        console.error(f"Network Error While Resolving Bedrock Skin For {gamertag}: {e}")

        return False, None, f"Network Error While Resolving Bedrock Skin For {gamertag}: {e}"
    except Exception as e:
        console.error(f"There Was An Unexpected Error While Resolving Bedrock Skin For {gamertag}: {e}")

        return False, None, f"There Was An Unexpected Error While Resolving Bedrock Skin For {gamertag}: {e}"

    console.log(f"[SUCCESS] Resolved Bedrock Skin For {gamertag}")

    return True, DOWNLOAD_PATH, "Bedrock Skin Resolved Successfully!"