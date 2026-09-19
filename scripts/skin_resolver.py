import importlib
import uuid
import tempfile
import httpx

from pathlib import Path
from urllib.parse import urlparse

from prayoadmii_lib import console
from prayoadmii_lib.configlib import tomlcfg


SERVICES = {
    "offline": "offline",
    "geyser": "geyser",
    "bedrock": "geyser",
    "mojang": "mojang",
}

MODULE_ROOT = "resolvers.{module}"


def is_url(value: str) -> bool:
    try:
        parsed = urlparse(value)

        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False


async def resolve_url(url: str) -> tuple[bool, Path | None, str]:
    config = tomlcfg.load("config.toml")

    tmp_dir = config.get_config("cache.tmp_folder_name", "head_server")
    user_agent = config.get_config("request.user_agent", "Head-Server")
    timeout = config.get_config("request.api_timeouts", 15)

    cache_dir = Path(tempfile.gettempdir()) / str(tmp_dir) / "module_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    skin_path = cache_dir / f"{uuid.uuid4()}.png"

    headers = {
        "User-Agent": user_agent,
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=int(timeout)) as client:
            response = await client.get(url, headers=headers)

            response.raise_for_status()

            if not response.content:
                return False, None, "Server returned an empty response."

            content_type = response.headers.get("content-type", "").lower()

            if not content_type.startswith("image/"):
                return False, None, f"Invalid content type: {content_type or 'unknown'}"

            skin_path.write_bytes(response.content)
    except httpx.HTTPStatusError as exc:
        return False, None, f"HTTP {exc.response.status_code}"
    except httpx.HTTPError as exc:
        return False, None, f"HTTP request failed: {exc}"
    except OSError as exc:
        return False, None, f"Failed to save skin: {exc}"

    return True, skin_path, f"Skin downloaded from {url}"


async def resolve_service(service: str, username: str) -> tuple[bool, Path | None, str]:
    module_name = SERVICES.get(service)

    if module_name is None:
        return False, None, f"Unknown skin service: {service}"

    try:
        module = importlib.import_module(MODULE_ROOT.format(module=module_name))
    except ImportError as exc:
        console.error(f"Failed to load skin service '{service}': {exc}")

        return False, None, f"Failed to load service: {service}"

    resolve = getattr(module, "resolve", None)

    if resolve is None or not callable(resolve):
        console.error(f"Skin service '{service}' does not have a callable resolve() function.")

        return False, None, f"Invalid skin service: {service}"

    try:
        result = await resolve(username)
    except Exception as exc:
        console.error(f"Skin service '{service}' failed for '{username}': {exc}")

        return False, None, str(exc)

    if not isinstance(result, tuple) or len(result) != 3:
        console.error(f"Skin service '{service}' returned an invalid result.")

        return False, None, f"Invalid result from service: {service}"

    return result


async def resolve_skin(username: str) -> tuple[bool, Path | None, str]:
    config = tomlcfg.load("config.toml")

    default = config.get_config("skins.default", "mojang")

    fallbacks = config.get_config("skins.fallbacks", ["offline"])

    if not isinstance(fallbacks, list):
        console.warn("skins.fallbacks must be a list. Using ['offline'] instead.")

        fallbacks = ["offline"]

    sources = [
        default,
        *fallbacks,
    ]

    for source in sources:
        if not isinstance(source, str):
            console.warn(f"Ignoring invalid skin source: {source!r}")

            continue

        source = source.strip()

        if not source:
            continue

        console.log(f"Trying skin source '{source}' for '{username}'...")

        if is_url(source):
            try:
                url = source.format(username=username)

            except (KeyError, ValueError) as exc:
                console.warn(f"Invalid URL template '{source}': {exc}")
                
                continue

            success, path, message = await resolve_url(url)
        else:
            success, path, message = await resolve_service(source, username)

        if success and path is not None:
            console.info(f"Skin resolved for '{username}' using '{source}'.")

            return True, path, message

        console.warn(f"Skin source '{source}' failed for '{username}': {message}")

    return False, None, f"No skin found for username: {username}"