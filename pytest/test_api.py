import pytest
import requests

@pytest.fixture
def bookmark_data():
    return {"title": "krish", "url":"krish.com", "description":"cool link"}

def bookmark_model():
    pass

def create_bookmark():
    pass
def delete_bookmark():
    pass
def update_bookmark():
    pass


def get_bookmark():
    url = "http://127.0.0.1:8000/bookmarks/0"
    response = requests.get(url)
    assert response.status_code == 200 

    assert response.headers["Content-Type"] == "application/json"

    data = response.json()  
    assert isinstance(data, dict)
    assert "id" in data
    assert "title" in data
    assert "url" in data
    assert "description" in data
    assert "timestamp" in data

    print("get_bookmark successful")


get_bookmark()
