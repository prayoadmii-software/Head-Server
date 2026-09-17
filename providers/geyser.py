import requests

from prayoadmii_lib import console

def resolve_geyser_url(gamertag: str):
    console.log(f"Getting Skins For: {str(gamertag)}")

    try:
        pending_xuid = requests.get(
            url=f"https://api.geysermc.org/v2/xbox/xuid/{str(gamertag)}",
            timeout=10
        )
        pending_xuid.raise_for_status()
        pending_xuid_json = pending_xuid.json()
        xuid = pending_xuid_json.get("xuid", None)

        if xuid is None:
            console.warn("No Bedrock XUID Provided!")

            return None

        pending_skin = requests.get(
            url=f"https://api.geysermc.org/v2/skin/{str(xuid)}",
            timeout=10
        )
        pending_skin.raise_for_status()
        pending_skin_json = pending_skin.json()
        texture_id = pending_skin_json.get("texture_id", None)

        if texture_id is None:
            console.warn("No Bedrock Texture ID Provided!")

            return None

        skin = f"http://textures.minecraft.net/texture/{texture_id}"

        console.log(f"Done Getting Skin For {str(gamertag)} Got {str(skin)}")

        return skin
    except Exception as e:
        console.warn(f"Got Error While Pulling Skin For {str(gamertag)} As {str(e)}")

        return None