from fastapi import Header, HTTPException, Security
from fastapi.security import APIKeyHeader


API_KEY = "my-secret-api-key"
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(API_KEY_NAME: str = Security(api_key_header)):
    if API_KEY_NAME != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return API_KEY_NAME

async def pagination(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

