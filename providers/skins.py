import requests

from prayoadmii_lib import console

from providers.geyser import resolve_geyser_url
from providers.mojang import resolve_mojang_url

def resolve_skin_url(username: str):
    console.log(f"Resolving Skin For: {username}")

    providers = [config.default] + config.fallbacks

    if username.startswith(str(config.bedrock_prefix)):
        console.info(f"{str(username)} Might Be A Bedrock Player! Threating Them As Bedrock Player!")

        skin_url = resolve_geyser_url(username.removeprefix(str(config.bedrock_prefix)))

        if skin_url is None:
            console.warn(f"Actually... {str(username)} Is Not Bedrock Player... Fixing It...")

            username = username.removeprefix(str(config.bedrock_prefix))
        else:
            console.log(f"Found {str(username)} As Bedrock Skin!")
            
            return skin_url

    for provider in providers:
        try:
            if provider.lower() == "bedrock":
                skin_url = resolve_geyser_url(username.removeprefix(str(config.bedrock_prefix)))

                if skin_url is None:
                    continue

                console.log(f"Found {str(username)} As Bedrock Skin!")
                
                return skin_url
            
            if provider.lower() == "mojang":
                skin_url = resolve_mojang_url(username)

                if skin_url is None:
                    continue

                console.log(f"Found {str(username)} As Mojang Skin!")
                
                return skin_url

            skin_url = provider.replace("{username}", username)

            response = requests.get(
                skin_url,
                timeout=10,
                headers={
                    "User-Agent": config.user_agent
                }
            )

            response.raise_for_status()

            console.log(f"Found {str(username)} On Other Skin Service With URL {str(skin_url)}")

            return skin_url
        except Exception as e:
            console.warn(f"Skin Provider Failed For {str(provider)} Got {str(e)}")

            continue
    console.warn(f"Could Not Find A Skin For {str(username)}")

    return None