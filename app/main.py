from fastapi import FastAPI
from schemas.bookmarks import Bookmark

app = FastAPI()

db = {"krish": ["https/krish/.com", "very cool site", "15:00"]}

@app.get("/")
def first_get():
    return {"hello" : "world"}

# query get
# bookmarks/1?q=hello
@app.get("/bookmarks/{bookmark_title}")
def read_bookmark(bookmark_title: str, q: str | None = None):
    url, description, timestamp = db.get(bookmark_title)
    return {"url": url, "description": description}

# put using pydantic
@app.put("/bookmarks/{bookmark_title}")
def create_bookmark(bookmark_title: str, bookmark: Bookmark):
    db[bookmark_title] = bookmark
    return {"bookmark_title": bookmark_title, "url": bookmark.url}



