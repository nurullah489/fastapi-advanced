from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.dependencies import verify_api_key, pagination, get_current_user, verify_all

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ------------- me as the current authenticated user-----------------------
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(verify_all)):
    return current_user

#------------- List all users with pagination and authentication -----------------------
@router.get("/", response_model=list[UserResponse], dependencies=[Depends(verify_all)])
async def list_users(params: dict = Depends(pagination), db: AsyncSession = Depends(get_db)):
    
    try:
        result = await db.execute(select(User).offset(params["skip"]).limit(params["limit"]))
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error occurred while fetching users")
    
    
# ------------- Get user by ID with authentication -----------------------
@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(verify_all)])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while fetching user: {e}")


# ------------- Create new user with background task and authentication -----------------------
# if user registration is active then create user is not required, otherwise we can use this endpoint for admin to create users
""" @router.post("/", response_model=UserResponse, status_code=201, dependencies=[Depends(verify_all)])
async def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
    
):
    try:
            
        result  = await db.execute(select(User).where(User.email == user.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        new_user = User(**user.model_dump(exclude_unset=True))
        db.add(new_user)
        await db.flush()
        await db.refresh(new_user)
        background_tasks.add_task(send_welcome_email, new_user.email, new_user.name)
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while creating user: {e}")       """  
        

# ------------- Update user with authentication -----------------------
@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(verify_all)])
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")
    try:            
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        for field, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, field, value) 
                    
        await db.flush()  
        await db.refresh(user)    
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while updating user: {e}")
    
    
# ------------- Delete user with authentication -----------------------
@router.delete("/{user_id}", status_code=204, dependencies=[Depends(verify_all)])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        await db.delete(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while deleting user: {e}")

def send_welcome_email(email: str, name: str):
    import time
    time.sleep(2) 
    print(f"Welcome email sent to {name} at {email}")
 