from fastapi import Header, HTTPException, Security, Header, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import select
from app.core.config import settings
from app.core.security import decode_access_token
from app.models.user import User


# --------- API Key Dependency ---------
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

#----------- Pagination Dependency ---------
async def pagination(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# --------- Authentication Dependency ---------
bearer_scheme = HTTPBearer(auto_error=False)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: AsyncSession = Depends(get_db)):
    try:        
        if not credentials:
            raise HTTPException(status_code=401, detail="Authorization token missing or invalid")
        token = credentials.credentials
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        user_id = int(payload.get("sub"))
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.active:
            raise HTTPException(status_code=403, detail="User is inactive")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while verifying token: {e}")
 

#---------- combined dependency for routes that require both API key and authentication ---------
async def verify_all(
    api_key: str = Security(verify_api_key),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:        
        if not api_key:
            raise HTTPException(status_code=401, detail=" API Key is missing or invalid")
        if api_key != settings.API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API Key")
        if not credentials:
            raise HTTPException(status_code=401, detail="Authorization token missing or invalid")
        token = credentials.credentials
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        user_id = int(payload.get("sub"))
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.active:
            raise HTTPException(status_code=403, detail="User is inactive")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while verifying credentials: {e}")
