from typing import Optional
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
	smtp_server: Optional[str] = None