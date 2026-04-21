import pytest
import requests

BASE_URL = "http://127.0.0.1:8000"

# pytest pytest/test_api.py -v 

@pytest.fixture
def bookmark_data():
    return {
        "title": "Test Bookmark",
        "url": "https://example.com",
        "description": "a test bookmark"
    }

@pytest.fixture
def created_bookmark(bookmark_data):
    response = requests.post(f"{BASE_URL}/bookmarks/", json=bookmark_data)
    assert response.status_code == 200
    bookmark = response.json()
    yield bookmark
    requests.delete(f"{BASE_URL}/bookmarks/{bookmark['id']}")


def test_create_bookmark(bookmark_data):
    response = requests.post(f"{BASE_URL}/bookmarks/", json=bookmark_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == bookmark_data["title"]
    assert "id" in data
    requests.delete(f"{BASE_URL}/bookmarks/{data['id']}")

def test_create_bookmark_duplicate_url(bookmark_data, created_bookmark):
    response = requests.post(f"{BASE_URL}/bookmarks/", json=bookmark_data)
    assert response.status_code == 409

def test_get_bookmark(created_bookmark):
    response = requests.get(f"{BASE_URL}/bookmarks/{created_bookmark['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created_bookmark["id"]

def test_get_bookmark_not_found():
    response = requests.get(f"{BASE_URL}/bookmarks/999999")
    assert response.status_code == 404

def test_update_bookmark(created_bookmark):
    updated = {"title": "Updated Title", "url": "https://updated-example.com", "description": "updated"}
    response = requests.put(f"{BASE_URL}/bookmarks/{created_bookmark['id']}", json=updated)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

def test_update_bookmark_not_found():
    response = requests.put(f"{BASE_URL}/bookmarks/999999", json={"title": "x", "url": "https://nowhere.com", "description": "x"})
    assert response.status_code == 404

def test_delete_bookmark(bookmark_data):
    create = requests.post(f"{BASE_URL}/bookmarks/", json=bookmark_data)
    bookmark_id = create.json()["id"]
    assert requests.delete(f"{BASE_URL}/bookmarks/{bookmark_id}").status_code == 200
    assert requests.get(f"{BASE_URL}/bookmarks/{bookmark_id}").status_code == 404

def test_delete_bookmark_not_found():
    assert requests.delete(f"{BASE_URL}/bookmarks/999999").status_code == 404

def test_search_bookmarks(created_bookmark):
    response = requests.get(f"{BASE_URL}/bookmarks/search/{created_bookmark['title']}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_bookmarks_no_filters():
    response = requests.get(f"{BASE_URL}/bookmarks")
    assert response.status_code == 200
    data = response.json()
    assert "bookmarks" in data
    assert "total_count" in data

def test_get_bookmarks_search_filter(created_bookmark):
    response = requests.get(f"{BASE_URL}/bookmarks", params={"search": "Test"})
    assert response.status_code == 200
    assert response.json()["total_count"] >= 1

def test_get_bookmarks_empty_search():
    response = requests.get(f"{BASE_URL}/bookmarks", params={"search": "zzznomatchzzz"})
    assert response.status_code == 200
    assert response.json()["total_count"] == 0
    assert response.json()["bookmarks"] == []

def test_add_tags(created_bookmark):
    tags = [{"title": "python"}, {"title": "testing"}]
    response = requests.post(f"{BASE_URL}/bookmarks/{created_bookmark['id']}/tags", json=tags)
    assert response.status_code == 200
    tag_titles = [t["title"] for t in response.json()["tags"]]
    assert "python" in tag_titles

def test_add_duplicate_tag(created_bookmark):
    tags = [{"title": "duplicate"}]
    requests.post(f"{BASE_URL}/bookmarks/{created_bookmark['id']}/tags", json=tags)
    response = requests.post(f"{BASE_URL}/bookmarks/{created_bookmark['id']}/tags", json=tags)
    assert response.status_code == 200
    assert [t["title"] for t in response.json()["tags"]].count("duplicate") == 1

def test_get_all_tags():
    response = requests.get(f"{BASE_URL}/tags")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_tag(created_bookmark):
    tags = [{"title": "to-delete"}]
    add = requests.post(f"{BASE_URL}/bookmarks/{created_bookmark['id']}/tags", json=tags)
    tag_id = next(t["id"] for t in add.json()["tags"] if t["title"] == "to-delete")
    response = requests.delete(f"{BASE_URL}/bookmarks/{created_bookmark['id']}/tags/{tag_id}")
    assert response.status_code == 200
    assert "to-delete" not in [t["title"] for t in response.json()["tags"]]
