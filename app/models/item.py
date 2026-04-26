from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str
    description: str = Field(..., max_length=300)
    price: float
    in_stock: bool = True

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    in_stock: bool
    
class ItemUpdate(BaseModel):
    name: str
    description: str = Field(..., max_length=300)
    price: float
    in_stock: bool