from enum import Enum
from typing import Optional, Union, Dict
from typing_extensions import Annotated
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


class Item(BaseModel):
	name: str
	description: Optional[str] = None
	price: float
	tax: Optional[float] = None

class ItemUpdate(BaseModel):
	name: Optional[str] = None
	description: Optional[str] = None
	price: Optional[float] = None
	tax: Optional[float] = None

class ItemResponse(BaseModel):
	message: str
	item: Item

class ItemQuery(BaseModel):
	skip: int = Field(default=0, ge=0, lt=100)
	limit: int = Field(default=10, ge=1, le=100)
	price: Optional[float] = Field(default=None, gt=0.0)


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
@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
	item_id: int
) -> Dict[str, Union[str, Item]]:
	if item_id not in items:
		raise HTTPException(status_code=404, detail=f"Item with ID={item_id} not found.")
	else:
		return ItemResponse(
			message="Item fetched successfully.",
			item=items[item_id]
		)


# Create a new item
@app.post("/create_items/", response_model=ItemResponse)
async def create_item(
	item: Item
) -> Dict[str, Union[str, Item]]:
	if any(existing_item.name == item.name for existing_item in items.values()):
		raise HTTPException(status_code=400, detail=f"Item with name={item.name} already exists.")		
	
	new_id = max(items.keys()) + 1
	items[new_id] = item
	
	return ItemResponse(
		message="Product created successfully",
		item=items[new_id]
	)


# Update an item
@app.put("/update/{item_id}", response_model=ItemResponse)
async def update_items(
	item_id: int,
	item_update: ItemUpdate
) -> Dict[str, Union[str, Item]]:
	if item_id not in items:
		raise HTTPException(status_code=400, detail=f"Item with ID={item_id} does not exist.")
	
	current_item = items[item_id]
	update_data = item_update.model_dump(exclude_unset=True)

	for field, value in update_data.items():
		setattr(current_item, field, value)
	
	return ItemResponse(
		message="Product updated successfully",
		item=current_item
	)


# Delete an item
@app.delete("/delete/{item_id}", response_model=ItemResponse)
async def delete_item(
	item_id: int
) -> Dict[str, Union[str, Item]]:
	if item_id not in items:
		raise HTTPException(status_code=400, detail=f"Item with ID={item_id} does not exist.")
	deleted_item = items[item_id]
	items.pop(item_id)

	return ItemResponse(
		message="Item successfully deleted.",
		item=deleted_item
	)


# Find item based on a query
@app.get("/query/")
async def item_query(
	filter_query: Annotated[ItemQuery, Query()]
) -> list[Item]:
	
	item_list = [item for item in items.values() if filter_query.price is None or item.price >= filter_query.price]
	return item_list
	

