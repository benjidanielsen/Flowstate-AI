from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v2", tags=["v2"])

# In-memory data store example
items_db = {}

class Item(BaseModel):
    id: int
    name: str
    description: str = None

class ItemCreate(BaseModel):
    name: str
    description: str = None

@router.get("/items", response_model=List[Item])
async def list_items():
    return list(items_db.values())

@router.post("/items", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    new_id = max(items_db.keys(), default=0) + 1
    new_item = Item(id=new_id, **item.dict())
    items_db[new_id] = new_item
    return new_item

@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

@router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = Item(id=item_id, **item.dict())
    items_db[item_id] = updated_item
    return updated_item

@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return None
