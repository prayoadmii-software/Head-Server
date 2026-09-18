from fastapi import FastAPI, status
from fastapi.responses import FileResponse

def setup(fapi: FastAPI, BASE_DIR):
    @fapi.get(path="/robots.txt")
    async def robots():
        return FileResponse(
            path=BASE_DIR / "assets" / "robots.txt",
            status_code=status.HTTP_200_OK
        )