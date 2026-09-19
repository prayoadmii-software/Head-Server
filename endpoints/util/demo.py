from fastapi import FastAPI, status
from fastapi.responses import FileResponse, RedirectResponse

def setup(fapi: FastAPI, BASE_DIR):
    @fapi.get(path="/demo.html")
    async def demo():
        return FileResponse(
            path=BASE_DIR / "assets" / "demo.html",
            status_code=status.HTTP_200_OK
        )

    @fapi.get(path="/demo")
    async def demo_redir():
        return RedirectResponse(
            url="/demo.html",
            status_code=status.HTTP_302_FOUND
        )