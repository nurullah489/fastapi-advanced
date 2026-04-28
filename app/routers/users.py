from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.dependencies import verify_api_key, pagination

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
    
):
    result  = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    new_user = User(**user.model_dump(exclude_unset=True))
    """ new_user = User(
        name=user.name,
        email=user.email,
        age=user.age,
        active=user.active
    ) """
    
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    background_tasks.add_task(send_welcome_email, new_user.email, new_user.name)
    return new_user


@router.get("/", response_model=list[UserResponse])
async def list_users(params: dict = Depends(pagination), db: AsyncSession = Depends(get_db), api_key: str = Depends(verify_api_key)):
    skip = params["skip"]
    limit = params["limit"]
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db), api_key: str = Depends(verify_api_key)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db), api_key: str = Depends(verify_api_key)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    """ # Update the user attributes
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, field, value) """
    user.name = user_update.name
    user.email = user_update.email 
    user.age = user_update.age
    user.active = user_update.active
    
    await db.flush()  
    await db.refresh(user)    
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), api_key: str = Depends(verify_api_key)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    await db.delete(user)
    

def send_welcome_email(email: str, name: str):
    import time
    time.sleep(2) 
    print(f"Welcome email sent to {name} at {email}")
    
""" @router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(user: UserCreate,
                        background_tasks: BackgroundTasks,
                        api_key: str = Depends(verify_api_key)):
    new_user = {
        "id": len(fake_db) + 1,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "active": user.active
    }
    background_tasks.add_task(send_welcome_email, user.email, user.name)
    return new_user """