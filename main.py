import requests
import uvicorn
import subprocess
import os

from prayoadmii_lib import console
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response, RedirectResponse, FileResponse

from renderer.head18 import render_head

from providers import skins

import config


subprocess.run(args="cls" if os.name == "nt" else "clear", shell=True)

app = FastAPI(
    title="Head Server",
    description="The All-In-One Minecraft Head/Face Skin Server!"
)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("favicon.ico")

@app.get("/", include_in_schema=False)
def favicon():
    return RedirectResponse(
        "https://github.com/prayoadmii-software/Head-Server",
        status_code=302
    )


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


# @app.get("/{username}")
# def get_redirect(username: str, just_redirect: bool = False):
#     if not just_redirect:
#         return get_head(username=username)

#     skin_url = skins.resolve_skin_url(username)

#     if skin_url is None:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Could Not Find Skin For: {str(username)}"
#         )

#     return RedirectResponse(
#         url=skin_url,
#         status_code=301
#     )


if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=str(config.host),
        port=int(config.port)
    )