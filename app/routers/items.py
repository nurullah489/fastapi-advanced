from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import verify_api_key, pagination
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy import select
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from app.models.item import Item

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)

def log_item_creation(item_id: int, item_name: str):
    import time
    time.sleep(2) 
    print(f"Item created: ID={item_id}, Name={item_name}")
    
@router.post("/", response_model=ItemResponse, dependencies=[Depends(verify_api_key)], status_code=201)
async def create_item(item: ItemCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    try:
        result_item = await db.execute(select(Item).where(Item.name == item.name))
        existing_item = result_item.scalar_one_or_none()
        if existing_item:
            raise HTTPException(status_code=400, detail="Item with this name already exists")    
        new_item = Item(**item.model_dump(exclude_unset=True))
        db.add(new_item)
        await db.flush()
        await db.refresh(new_item)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating item: {e}")
    background_tasks.add_task(log_item_creation, new_item.id, new_item.name)
    return new_item
 
@router.get("/", response_model=list[ItemResponse], dependencies=[Depends(verify_api_key)])
async def list_items(params: dict = Depends(pagination), db: AsyncSession = Depends(get_db)):
    try:
        skip = params["skip"]
        limit = params["limit"]
        result = await db.execute(select(Item).offset(skip).limit(limit))
        items = result.scalars().all()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching items: {e}")    

@router.get("/{item_id}", response_model=ItemResponse, dependencies=[Depends(verify_api_key)])
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    try:        
        result = await db.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
        return item
    except HTTPException:
        raise  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching item: {e}")

@router.put("/{item_id}", response_model=ItemResponse, dependencies=[Depends(verify_api_key)])
async def update_item(item_id: int, item_update: ItemUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
        for field, value in item_update.model_dump().items():
            setattr(item, field, value)
        await db.flush()
        await db.refresh(item)
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating item: {e}")
 
@router.delete("/{item_id}", dependencies=[Depends(verify_api_key)], status_code=204)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
        await db.delete(item)
        await db.flush()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting item with ID {item_id}: {e}")