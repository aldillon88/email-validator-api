import httpx

url = "http://127.0.0.1:8000/create_items/"
payload = {
	"name": "Foo",
	"description": "An optional description",
	"price": 45.2,
	"tax": 3.5
}

response = httpx.post(url, json=payload)
print(response.status_code, response.text)