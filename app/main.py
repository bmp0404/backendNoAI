from fastapi import FastAPI, Depends, HTTPException
from schemas.schemas import BookmarkBase, BookmarkCreate, Bookmark
from models.models import Bookmark as BookmarkModel
from models.models import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from typing import List
import logging
from starlette.middleware.base import BaseHTTPMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

# logging file points to app.log, only accepts .info
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def get_db(): 
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def first_get():
    return {"hello" : "world"}

@app.middleware("http")
async def log_requests(request, call_next):
    client_ip = request.client.host
    method = request.method
    url = request.url.path

    logger.info(f"Request: {method} {url} from {client_ip}")
    response = await call_next(request)
    logger.info(f"Response: {method} {url} returned {response.status_code} to {client_ip}")
    return response

# SEARCH by title (returns list of matches)
@app.get("/bookmarks/search/{bookmark_title}", response_model=List[Bookmark])
def search_bookmarks_by_title(bookmark_title: str, db: Session = Depends(get_db)):
    bookmarks = db.query(BookmarkModel).filter(BookmarkModel.title.contains(bookmark_title)).all()
    return bookmarks

@app.get("/bookmarks/{bookmark_id}", response_model = Bookmark)
def read_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    if not bookmark_id == 0:
        bookmark = db.query(BookmarkModel).filter(BookmarkModel.id == bookmark_id).first()
    if not bookmark:
         raise HTTPException(status_code=404, detail="bookmark not found")
    return bookmark

@app.post("/bookmarks/", response_model = Bookmark)
def create_bookmark(bookmark: BookmarkCreate, db: Session = Depends(get_db)):
    url_exists =db.query(BookmarkModel).filter(BookmarkModel.url == bookmark.url).first()
    if (url_exists):
        raise HTTPException(status_code=409, detail="url already exists")
    db_bookmark = BookmarkModel(**bookmark.model_dump())
    db.add(db_bookmark) # add to session
    db.commit() # commit the transaction to DB
    db.refresh(db_bookmark) # refresh to get the latest state
    return db_bookmark


@app.put("/bookmarks/{bookmark_id}", response_model = BookmarkBase)
def update_bookmark(bookmark_id: int, bookmark: BookmarkBase, db : Session = Depends(get_db)):
    url_exists = db.query(BookmarkModel).filter(BookmarkModel.url == bookmark.url, BookmarkModel.id != bookmark_id).first()
    if (url_exists):
        raise HTTPException(status_code=409, detail="url already exists")
    db_bookmark = db.query(BookmarkModel).filter(BookmarkModel.id == bookmark_id).first()
    if not db_bookmark:
         raise HTTPException(status_code=404, detail="bookmark not found")
    for k, v in bookmark.model_dump().items():
        setattr(db_bookmark, k, v)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark



@app.delete("/bookmarks/{bookmark_id}", response_model = Bookmark)
def delete_user(bookmark_id: int, db: Session = Depends(get_db)):
    db_bookmark = db.query(BookmarkModel).filter(BookmarkModel.id == bookmark_id).first()
    if not db_bookmark:
        raise HTTPException(status_code=404, detail="bookmark not found")
    db.delete(db_bookmark)
    db.commit()
    return db_bookmark








