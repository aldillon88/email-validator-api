from enum import Enum
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel



class Item(BaseModel):
	name: str
	description: Optional[str] = None
	price: float
	tax: Optional[float] = None


items = {
	0: Item(name='Product 1', description='This is Product 1', price=15.00, tax=2),
	1: Item(name='Product 2', description='This is Product 2', price=25.00, tax=4),
	2: Item(name='Product 3', description='This is Product 3', price=35.00, tax=5),
	3: Item(name='Product 4', description='This is Product 4', price=45.00, tax=7),
	4: Item(name='Product 5', description='This is Product 5', price=50.00, tax=8)
}


app = FastAPI()

@app.get("/")
async def root():
	return {'message': "This is the root URL"}


# Read all items
@app.get("/items/")
async def list_items(
	skip: int = 0,
	limit: int = 10
) -> list[Item]:
	items_list = list(items.values())[skip: skip + limit]
	return items_list


# Read a single item by id
@app.get("/items/{item_id}")
async def get_item(item_id: int) -> Item:
	if item_id not in items:
		raise HTTPException(status_code=404, detail=f"Item with ID={item_id} not found.")
	else:
		return items[item_id]


# Create a new item
@app.post("/create_items/")
async def create_item(item: Item) -> list[Item]:
	if any(existing_item.name == item.name for existing_item in items.values()):
		raise HTTPException(status_code=400, detail=f"Item with name={item.name} already exists.")		
	
	new_id = max(items.keys()) + 1
	items[new_id] = item
	
	return [item for item in items.values()]



# Update an item



# Delete an item


