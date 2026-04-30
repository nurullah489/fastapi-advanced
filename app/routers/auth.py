from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import verify_api_key
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from sqlalchemy import select

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

"""
    Register and login endpoints are public but require API key to check only authorized client app can register user.
    Once user is registered or logged in, they receive a JWT token which they can use to access protected routes.
    The verify_all dependency ensures that both API key and valid token are required for protected routes.
    
"""




@router.post("/register", response_model=TokenResponse, status_code=201, dependencies=[Depends(verify_api_key)])
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(User).where(User.email == request.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while checking user: {e}")

    hashed_pwd = hash_password(request.password)
    new_user = User(
        name=request.name,
        email=request.email,
        age=request.age,
        active= True,
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    
    token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
    return TokenResponse(access_token=token, token_type="bearer")

@router.post("/login", response_model=TokenResponse, dependencies=[Depends(verify_api_key)])
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while logging in: {e}")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token)