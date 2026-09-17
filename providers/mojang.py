import requests
import base64
import json

from prayoadmii_lib import console


def resolve_mojang_url(username: str):
    console.log(f"Getting Skins For: {str(username)}")

    try:
        pending_data = requests.get(
            url=f"https://api.mojang.com/users/profiles/minecraft/{username}",
            timeout=10
        )
        pending_data.raise_for_status()
        pending_data_json = pending_data.json()

        uuid = pending_data_json.get("id")

        if uuid is None:
            console.warn("No Valid Mojang UUID Received!")

            return None

        pending_info = requests.get(
            url=f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}",
            timeout=10
        )
        pending_info.raise_for_status()
        pending_info_json = pending_info.json()

        properties = pending_info_json.get("properties")

        if not isinstance(properties, list):
            console.warn("No Valid Mojang Player Properties Received!")

            return None

        textures_property = next(
            (
                property_data
                for property_data in properties
                if property_data.get("name") == "textures"
            ),
            None
        )

        if textures_property is None:
            console.warn("No Valid Mojang Textures Property Received!")

            return None

        encoded_texture_data = textures_property.get("value")

        if encoded_texture_data is None:
            console.warn("No Valid Player Texture Data Received!")

            return None

        decoded_texture_data = base64.b64decode(
            encoded_texture_data
        ).decode("utf-8")

        texture_json = json.loads(decoded_texture_data)

        skin_url = (
            texture_json
            .get("textures", {})
            .get("SKIN", {})
            .get("url")
        )

        if skin_url is None:
            console.warn("No Valid Mojang Skin URL Received!")

            return None

        console.log(f"Done Getting Skin For {str(username)} Got {str(skin_url)}")

        return skin_url
    except Exception as e:
        console.warn(f"There Are An Error While Trying To Get Skin For {str(username)} As {str(e)}")

        return None