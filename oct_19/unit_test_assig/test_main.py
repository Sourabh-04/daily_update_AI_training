from fastapi.testclient import TestClient
from main2 import my_app

client = TestClient(my_app)




def test_post_task():
    response = client.post("/task",
                          json={"id":2,"title":"Prepare report","status":'Pending'})
    assert response.status_code == 200

def test_get_task_with_id():

    client.post(
        "/task",
        json={
            "id": 1,
            "title": "Learn FastAPI",
            "status": "Pending"
        }
    )

    response = client.get("/task/1")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1

def test_wrong_id():
    response = client.get("/task/6")
    assert response.status_code == 404


def test_get_task():
    response = client.get("/task")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 1

def test_wrong_format():
    response = client.post("/task",
       json={"id":"df","title":"Prepare report","status":'Pending'})
    assert response.status_code == 422

def test_put():
    response = client.put("/task/2",
          json={"id":2,"title":"Prepare report","status":'Comlete'})
    assert response.status_code == 200
    response = client.get("/task/2")
    data = response.json()
    assert data["id"] == 2
    assert data["status"]=="Comlete"

def test_delete():
    response = client.delete("/task/2")
    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted successfully"}

def test_get():
    response = client.get("/task/2")
    assert response.status_code == 404

