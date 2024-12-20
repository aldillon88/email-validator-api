from typing import Dict
from fastapi import FastAPI, HTTPException
import re
import dns.resolver
from models.models import *


app = FastAPI()

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
		mx_records = dns.resolver.resolve(domain, 'MX')
		# Choose the highest-priority MX server (lowest priority value) for the connection.
		smtp_server = str(sorted(mx_records, key=lambda r: r.preference)[0].exchange)
		return DnsResponse(
			email=request.email,
			message=f"The domain {domain} has valid MX records",
			smtp_server=smtp_server
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
	
