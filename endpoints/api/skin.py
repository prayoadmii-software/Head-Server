import os

from pathlib import Path
from fastapi import FastAPI, status
from fastapi.responses import FileResponse, JSONResponse

from scripts import skin_resolver
from renderer.modern import iilayer

def setup(fapi: FastAPI, BASE_DIR: Path):
    @fapi.get(path="/{username}.png")
    async def skin(username: str):
        success, skin_path, message = await skin_resolver.resolve_skin(username)

        if not success or skin_path is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "message": message,
                },
            )

        success, face_path, message = await iilayer.render_skin_face(skin_path)

        if not success or face_path is None:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "message": message,
                },
            )

        os.remove(skin_path)

        return FileResponse(
            path=face_path,
            media_type="image/png",
            filename=f"{username}.png",
            content_disposition_type="inline",
        )