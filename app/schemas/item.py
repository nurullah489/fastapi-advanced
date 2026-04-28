from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=300)
    price: float
    in_stock: bool = True

class ItemUpdate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=300)
    price: float
    in_stock: bool

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    in_stock: bool

model_config = {
    "from_attributes": True
}
