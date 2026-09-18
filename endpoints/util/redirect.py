from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

def setup(fapi: FastAPI, BASE_DIR):
    @fapi.get("/", include_in_schema=False)
    async def redirect():
        return RedirectResponse(
            "https://github.com/prayoadmii-software/Head-Server",
            status_code=status.HTTP_302_FOUND
        )