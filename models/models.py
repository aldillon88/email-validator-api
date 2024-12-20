from typing import Optional
from pydantic import BaseModel

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