from fastapi import Header, HTTPException
from core.config import TG_KEY_API


async def verify_api_key(api_key: str = Header(alias="Api-key")) -> None:
    if api_key != TG_KEY_API:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")
