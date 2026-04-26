from fastapi import FastAPI
from app.routers import users, items

app  = FastAPI(
    title="FastAPI Learning",
    description="Production-grade FastAPI project.", 
    version="1.0.0"
)

app.include_router(users.router)
app.include_router(items.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the User Management API!"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}