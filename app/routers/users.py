from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.dependencies import verify_api_key, pagination
from app.models.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

fake_db: list[dict] = []

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, api_key: str = Depends(verify_api_key)):
    new_user = {
        "id": len(fake_db) + 1,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "active": user.active
    }
    fake_db.append(new_user)
    return new_user

@router.get("/", response_model=list[UserResponse])
async def list_users(params: dict = Depends(pagination)):
    skip = params["skip"]
    limit = params["limit"]
    return fake_db[skip:skip + limit]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    for user in fake_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail=f"User {user_id} not found")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate):
    for user in fake_db:
        if user["id"] == user_id:
            user["name"] = user_update.name
            user["email"] = user_update.email
            user["age"] = user_update.age
            user["active"] = user_update.active
            return user
    raise HTTPException(status_code=404, detail=f"User {user_id} not found")

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    for index, user in enumerate(fake_db):
        if user["id"] == user_id:
            del fake_db[index]
            return
    raise HTTPException(status_code=404, detail=f"User {user_id} not found")

def send_welcome_email(email: str, name: str):
    import time
    time.sleep(2) 
    print(f"Welcome email sent to {name} at {email}")
    
@router.post("/register", response_model=UserResponse, status_code=201)
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
    fake_db.append(new_user)
    background_tasks.add_task(send_welcome_email, user.email, user.name)
    return new_user