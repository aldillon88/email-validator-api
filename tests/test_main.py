from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test "/format-check/"
def test_format_check_endpoint():
    route = "/format-check/"
    json = {
        "email": "abc@gmail.com"
    }
    response = client.post(url=route, json=json)
    assert response.status_code == 200

# Test "/dns-check/"
def test_dns_check_endpoint():
    route = "/dns-check/"
    json = {
        "email": "abc@gmail.com"
    }
    response = client.post(url=route, json=json)
    assert response.status_code == 200