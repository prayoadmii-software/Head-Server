import base64
import json
import tempfile
import uuid
import httpx

from pathlib import Path

from prayoadmii_lib import console
from prayoadmii_lib.configlib import tomlcfg


async def resolve_mojang_skin(username: str) -> tuple[bool, Path | None, str]:
    CONFIG = tomlcfg.load("config.toml")

    TMP_DIR = CONFIG.get_config("cache.tmp_folder_name", "head_server")
    USR_AGENT = CONFIG.get_config("request.user_agent")
    TIMEOUT = CONFIG.get_config("request.api_timeouts", 15)
    HEADERS = {
        "User-Agent": str(USR_AGENT)
    }

    username = username.strip()

    if not username:
        return False, None, "No Username Provided!"

    console.log(f"Getting Java Edition Skin For {username}")

    DOWNLOAD_PATH = Path(tempfile.gettempdir()) / str(TMP_DIR) / "module_cache" / f"{uuid.uuid4()}.png"
    DOWNLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        async with httpx.AsyncClient(timeout=float(TIMEOUT), headers=HEADERS) as client:
            console.log(f"[NOW PENDING] Get UUID Of {username}")

            response = await client.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")

            response.raise_for_status()

            mojang_profile = response.json()

            console.log(f"[LOADING] Get UUID Of {username}")

            mojang_uuid = mojang_profile.get("id")

            if mojang_uuid is None:
                console.error("There's No Valid UUID Returned From Mojang API!")

                return False, None, "There's No Valid UUID Returned From Mojang API!"

            console.log(f"[DONE] Get UUID Of {username}")


            console.log(f"[NOW PENDING] Get Texture Data Of {mojang_uuid}")

            response = await client.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{mojang_uuid}")

            response.raise_for_status()

            session_profile = response.json()

            console.log(f"[LOADING] Get Texture Data Of {mojang_uuid}")

            properties = session_profile.get("properties", [])

            textures_property = next(
                (
                    property_data
                    for property_data in properties
                    if property_data.get("name") == "textures"
                ),
                None
            )

            if textures_property is None:
                console.error("There's No Textures Property Returned From Mojang Session Server!")

                return False, None, "There's No Textures Property Returned From Mojang Session Server!"

            encoded_textures = textures_property.get("value")

            if encoded_textures is None:
                console.error("There's No Valid Textures Property Value Returned!")

                return (
                    False,
                    None,
                    "There's No Valid Textures Property Value Returned!"
                )

            console.log(
                f"[DONE] Get Texture Data Of {mojang_uuid}"
            )


            console.log(f"[NOW PENDING] Decode Texture Data Of {mojang_uuid}")

            try:
                decoded_textures = base64.b64decode(encoded_textures).decode("utf-8")

                textures_data = json.loads(decoded_textures)
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as e:
                console.error(f"Could Not Decode Mojang Texture Property: {e}")

                return False, None, f"Could Not Decode Mojang Texture Property: {e}"

            console.log(f"[LOADING] Decode Texture Data Of {mojang_uuid}")

            textures = textures_data.get("textures", {})
            skin_data = textures.get("SKIN")

            if skin_data is None:
                console.error("There's No Skin Texture Returned From Mojang!")

                return False, None, "There's No Skin Texture Returned From Mojang!"

            skin_url = skin_data.get("url")

            if skin_url is None:
                console.error("There's No Valid Skin URL Returned From Mojang!")

                return False, None, "There's No Valid Skin URL Returned From Mojang!"

            console.log(f"[DONE] Decode Texture Data Of {mojang_uuid}")


            console.log(f"[NOW PENDING] Download Java Skin Of {username}")

            response = await client.get(skin_url)

            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()

            if not content_type.startswith("image/"):
                console.error(f"Minecraft Texture Server Returned Unexpected Content-Type: {content_type}")

                return False, None, f"Minecraft Texture Server Returned Unexpected Content-Type: {content_type}"

            DOWNLOAD_PATH.write_bytes(response.content)

            console.log(f"[DONE] Download Java Skin Of {username}")
    except httpx.HTTPStatusError as e:
        console.error(f"HTTP Error While Resolving Java Skin For {username}: {e}")

        return False, None, f"HTTP Error While Resolving Java Skin For {username}: {e}"
    except httpx.RequestError as e:
        console.error(f"Network Error While Resolving Java Skin For {username}: {e}")

        return False, None, f"Network Error While Resolving Java Skin For {username}: {e}"
    except Exception as e:
        console.error(f"There Was An Unexpected Error While Resolving Java Skin For {username}: {e}")

        return False, None, f"There Was An Unexpected Error While Resolving Java Skin For {username}: {e}"

    console.log(f"[SUCCESS] Resolved Java Skin For {username}")

    return True, DOWNLOAD_PATH, "Java Skin Resolved Successfully!"