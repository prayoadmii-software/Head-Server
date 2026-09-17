import requests
import uvicorn
import subprocess
import os
import importlib

from pathlib import Path
from prayoadmii_lib import console
from prayoadmii_lib.configlib import tomlcfg
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response, RedirectResponse

from renderer.head18 import render_head

from providers import skins

subprocess.run(args="cls" if os.name == "nt" else "clear", shell=True)

configs = tomlcfg.load("config.toml")

BASE_DIR = Path(__file__).resolve().parent
_LOADED_MODULES = set()

app = FastAPI(
    title="Head Server",
    description="The All-In-One Minecraft Head/Face Skin Server!"
)

def LoadModules(app: FastAPI, project_base_dir: Path, base_path: str):
    base_dir = Path(__file__).resolve().parent
    target_dir = base_dir / base_path

    for root, _, files in os.walk(target_dir):
        for file in files:
            if not file.endswith(".py") or file == "__init__.py":
                continue

            full_path = Path(root) / file

            module_path = full_path.relative_to(base_dir)
            module_path = ".".join(module_path.with_suffix("").parts)

            if module_path in _LOADED_MODULES:
                continue

            try:
                module = importlib.import_module(module_path)
                setup = getattr(module, "setup", None)

                if setup is None:
                    console.warn(f"There Are No setup() In {module_path}")

                    continue

                if not callable(setup):
                    console.warn(f"setup In {module_path} Is Not Callable!")

                    continue

                setup(app, project_base_dir)

                _LOADED_MODULES.add(module_path)

                console.info(f"Loaded Module: {module_path}")
            except Exception as e:
                console.warn(f"Failed To Load {module_path} As: {e}")

LoadModules(app, BASE_DIR, "endpoints")

@app.get("/{username}.png")
def get_head(username: str, mode: str = Query(default=None)):
    skin_mode = (
        mode
        if mode is not None
        else config.default_skin_mode
    ).lower()

    if skin_mode not in (
        "head",
        "head-1-8"
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported Skin Mode: {skin_mode}"
        )

    skin_url = skins.resolve_skin_url(
        username
    )

    if skin_url is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could Not Find Skin For {username}"
        )

    try:
        image = render_head(
            skin_url
        )

        return Response(
            content=image,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=300"
            }
        )

    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to download skin: {e}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to render skin: {e}"
        )

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=str(configs.get_config("web.bind", "0.0.0.0")),
        port=int(configs.get_config("web.port", 7500))
    )