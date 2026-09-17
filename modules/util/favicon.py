from fastapi import FastAPI, status
from fastapi.responses import FileResponse

def setup(fapi: FastAPI, BASE_DIR):
    @fapi.get(path="/favicon.ico")
    async def favicon():
        return FileResponse(
            path=BASE_DIR / "favicon.ico",
            status_code=status.HTTP_200_OK
        )