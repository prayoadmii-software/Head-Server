import asyncio
import tempfile
import uuid

from pathlib import Path
from prayoadmii_lib import console
from prayoadmii_lib.configlib import tomlcfg
from PIL import Image

async def render_skin_face(skin_path: Path) -> tuple[bool, Path | None, str]:
    CONFIG = tomlcfg.load("config.toml")

    TMP_FILE = Path(tempfile.gettempdir()) / str(CONFIG.get_config("cache.tmp_folder_name", "head_server")) / "module_cache" / f"{uuid.uuid4()}.png"
    TMP_FILE.parent.mkdir(parents=True, exist_ok=True)
 
    def _process_image():
        console.log("Loading Skin File...")

        try:
            skin = Image.open(skin_path).convert("RGBA")

            base_face = skin.crop((8, 8, 16, 16))
            
            img_resized = base_face.resize((int(CONFIG.get_config("output.weight", 128)), int(CONFIG.get_config("output.height", 128))), Image.NEAREST)
        except Exception as e:
            console.error(f"There's Error While Loading Skin File As: {str(e)}")

            return False, None, "Error While Loading Skin File"

        console.log("Saving Skin File...")

        try:
            img_resized.save(TMP_FILE)
        except Exception as e:
            console.error(f"There's Error While Saving Skin File As: {str(e)}")
            
            return False, None, "Error While Saving Skin File"

        return True, TMP_FILE, "Done!"

    success, path, message = await asyncio.to_thread(_process_image)

    if success:
        console.log("Done!")

    return success, path, message