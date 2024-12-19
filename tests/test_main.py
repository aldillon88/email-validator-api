from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Test root "/"
def test_root_enpoint():
    route = "/"
    response = client.get(url=route)
    assert response.status_code == 200


# Test "/items"
def test_items_endpoint():
    route = "/items/"
    params = {
        "skip": 1,
        "limit": 3
    }
    response = client.get(url=route, params=params)
    assert response.status_code == 200
    assert len(response.json()) == params["limit"]


# Test "/create_items/"
def test_create_items_endpoint():
    route = "/create_items/"
    payload = {
        "name": "Foo",
        "description": "An optional description",
        "price": 45.2,
        "tax": 3.5
    }
    response = client.post(url=route, json=payload)
    assert response.status_code == 200

# Test "/update/{item_id}"
def test_update_items_endpoint():
    item_id = 2
    route = f"/update/{item_id}"
    payload = {
        "price": 40.00,
        "tax": 7.50
    }
    response = client.put(url=route, json=payload)
    assert response.status_code == 200

# Test "/delete/{item_id}"
def test_delete_item_endpoint():
    item_id = 2
    route = f"/delete/{item_id}"
    response = client.delete(url=route)
    assert response.status_code == 200

# Test "/query/"
def test_query_items_endpoint():
    route = "/query/"
    params = {
        "skip": 1,
        "limit": 3,
        "price": 20
    }
    response = client.get(url=route, params=params)
    assert response.status_code == 200