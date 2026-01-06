from fastapi import HTTPException
from starlette.requests import Request
from config.settings import settings


def require_token(request: Request):
    token = request.headers.get("X-API-Token")
    if token != settings.API_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")
