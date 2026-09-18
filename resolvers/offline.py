import hashlib
import uuid
import tempfile
import shutil

from pathlib import Path
from prayoadmii_lib import console
from prayoadmii_lib.configlib import tomlcfg

SKIN_LOCATION = [
    "slim/alex",
    "slim/ari",
    "slim/efe",
    "slim/kai",
    "slim/makena",
    "slim/noor",
    "slim/steve",
    "slim/sunny",
    "slim/zuri",
    "wide/alex",
    "wide/ari",
    "wide/efe",
    "wide/kai",
    "wide/makena",
    "wide/noor",
    "wide/steve",
    "wide/sunny",
    "wide/zuri",
]

async def resolve_offline_skin(username: str) -> tuple[bool, Path | None, str]:
    CONFIG = tomlcfg.load("config.toml")
    
    TMP_DIR = CONFIG.get_config("cache.tmp_folder_name", "head_server")

    RUN_FOLDER = Path.cwd()

    console.log(f"Getting Offline Mode Skin For {username}")

    digest = bytearray(
        hashlib.md5(
            f"OfflinePlayer:{username}".encode("utf-8")
        ).digest()
    )

    digest[6] = (digest[6] & 0x0F) | 0x30
    digest[8] = (digest[8] & 0x3F) | 0x80

    player_uuid = uuid.UUID(bytes=bytes(digest))
    value = player_uuid.int

    most_sig_bits = (value >> 64) & 0xFFFFFFFFFFFFFFFF
    least_sig_bits = value & 0xFFFFFFFFFFFFFFFF

    xor_bits = most_sig_bits ^ least_sig_bits

    uuid_hash = (
        xor_bits ^ ((xor_bits >> 32) & 0xFFFFFFFF)
    ) & 0xFFFFFFFF

    if uuid_hash & 0x80000000:
        uuid_hash -= 0x100000000

    index = uuid_hash % len(SKIN_LOCATION)

    if index < 0:
        index += 18

    SKIN_PATH = RUN_FOLDER / "skins" / "defaults" / f"{SKIN_LOCATION[index]}.png"

    TMP_FILE = Path(tempfile.gettempdir()) / str(TMP_DIR) / "module_cache" / f"{uuid.uuid4()}.png"

    TMP_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not SKIN_PATH.is_file():
        console.error(f"Offline Skin Not Found: {SKIN_PATH}")

        return False, None, "Offline Skin File Not Found!"

    shutil.copy2(SKIN_PATH, TMP_FILE)
    
    console.log(f"[DONE] Getting Offline Mode Skin For {username}")

    return True, TMP_FILE, "Done!"