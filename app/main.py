from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import users, items
from app.database import Base, engine


app  = FastAPI(
    title="FastAPI Advanced",
    description="Production-grade FastAPI with PostgreSQL.", 
    version="2.0.0"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:        
        async with engine.begin() as conn:
            pass
    except Exception as e:
        print(f"Error during startup: {e}")
        



@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the User Management API!"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

app.include_router(users.router)
app.include_router(items.router)