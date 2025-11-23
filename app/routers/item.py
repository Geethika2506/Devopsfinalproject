from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Item(BaseModel):
    title: str
    description: str

items_db = {}
next_id = 0

@router.post("/items")
def create_item(item: Item):
    global next_id
    next_id += 1
    new_item = {"id": next_id, **item.dict()}
    items_db[next_id] = new_item
    return new_item

@router.get("/items/{item_id}")
def get_item(item_id: int):
    return items_db[item_id]
