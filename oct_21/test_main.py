from fastapi.testclient import TestClient
from fast_api_uni import app


client = TestClient(app)

def test_get_product():
    response = client.get("/products")

    assert response.status_code == 200
def test_add_product():
    response = client.post("/products",
                           json={'id':2 , 'name':'lapo','price':2000})
    assert response.status_code == 200

    data = response.json()
    assert data['id']==2
    assert data['name']=='lapo'
    assert data['price']==2000



def test_invalid_product():
    response = client.post(
        "/products",
        json={
            "id": 103,
            "name": "Speaker",
            "price": "hello"
        }
    )

    assert response.status_code == 422