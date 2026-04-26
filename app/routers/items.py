from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.dependencies import verify_api_key, pagination
from app.models.item import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)
fake_db_items: list[dict] = []

def log_item_creation(item_id: int, item_name: str):
    import time
    time.sleep(2) 
    print(f"Item created: ID={item_id}, Name={item_name}")
    
@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate, background_tasks: BackgroundTasks, api_key: str = Depends(verify_api_key)):
    new_item = {
        "id": len(fake_db_items) + 1,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "in_stock": item.in_stock
    }
    fake_db_items.append(new_item)
    background_tasks.add_task(log_item_creation, new_item["id"], new_item["name"])
    return new_item
 
@router.get("/", response_model=list[ItemResponse])
async def list_items(params: dict = Depends(pagination)):
    skip = params["skip"]
    limit = params["limit"]
    return fake_db_items[skip:skip + limit]

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    for item in fake_db_items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item_update: ItemUpdate):
    for item in fake_db_items:
        if item["id"] == item_id:
            item["name"] = item_update.name
            item["description"] = item_update.description
            item["price"] = item_update.price
            item["in_stock"] = item_update.in_stock
            return item
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int):
    for index, item in enumerate(fake_db_items):
        if item["id"] == item_id:
            del fake_db_items[index]
            return
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")