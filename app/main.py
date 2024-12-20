from typing import Optional, Union, Dict
from typing_extensions import Annotated
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import re
import dns.resolver


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

class EmailFormatRequest(BaseModel):
	email: str

class EmailFormatResponse(BaseModel):
	email: str
	valid_length: bool
	valid_format: bool
	local_part: Optional[str] = None
	domain: Optional[str] = None
	valid_domain: Optional[bool] = None

class DnsRequest(BaseModel):
	email: str

class DnsResponse(BaseModel):
	email: str
	message: str


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
	

# Check email format
@app.post("/format-check/", response_model=EmailFormatResponse)
async def email_pattern_validation(request: EmailFormatRequest) -> Dict[str, EmailFormatResponse]:

	if not request.email:
		raise HTTPException(status_code=400, detail="Email missing from function arguments.")
	
	if len(request.email) > 254:  # RFC 5321
		valid_length = False
	else:
		valid_length = True
		
	pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
	
	if re.match(pattern, request.email):
		valid_format = True
	else:
		valid_format = False
	
	# Additional specific checks for better error messages
	if '@' not in request.email:
		local_part = None
		domain = None
		valid_domain = None
	else:
		local_part, _, domain = request.email.partition('@')
		if '.' not in domain:
			valid_domain = False
		else:
			valid_domain = True
	
	return EmailFormatResponse(
		email=request.email,
		valid_length=valid_length,
		valid_format=valid_format,
		local_part=local_part,
		domain=domain,
		valid_domain=valid_domain
	)

# DNS query using dnspython
@app.post("/dns-check/", response_model=DnsResponse)
def validate_email_dns(request: DnsRequest) -> Dict[str, DnsResponse]:

	try:
		domain = request.email.split("@")[1]
	
	except:
		return DnsResponse(
			email=request.email,
			message=f"An issue exists with the email {request.email}. Please check the email."
		)

	try:
		dns.resolver.resolve(domain, 'MX')
		return DnsResponse(
			email=request.email,
			message=f"The domain {domain} has valid MX records"
		)
	
	except dns.resolver.NXDOMAIN: # The domain doesn't exist
		return DnsResponse(
			email=request.email,
			message=f"The domain {domain} does not exist"
		)
	
	except dns.resolver.NoAnswer: # No MX records
		return DnsResponse(
			email=request.email,
			message=f"The domain {domain} has no MX records"
		)
	
	except dns.exception.Timeout: # DNS query timed out
		return DnsResponse(
			email=request.email,
			message=f"The DNS query for domain {domain} timed out"
		)
	
