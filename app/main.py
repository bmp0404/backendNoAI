from fastapi import FastAPI, Depends, HTTPException
from schemas.schemas import BookmarkBase, BookmarkCreate, Bookmark, TagBase, Tag, BookmarkList
from models.models import Bookmark as BookmarkModel
from models.models import Tag as TagModel
from models.models import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
import logging
from enum import Enum
from datetime import datetime

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

class SortBy(str, Enum):
    title = "title"
    url = "url"
    description = "description"
    timestamp = "timestamp"
    tags = "tags"

class OrderBy(str, Enum):
    ascending = "ascending"
    descending = "descending"

# get /bookmarks
@app.get("/bookmarks", response_model=BookmarkList)
def get_bookmarks(search: str | None = None,
    tag: str | None = None,
    saved_after: datetime | None = None,
    saved_before: datetime | None = None,
    sort_by: SortBy | None = None,
    order_by: OrderBy | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)):
    bookmarks = db.query(BookmarkModel)
    if search:
        bookmarks = bookmarks.filter(
            or_(
                BookmarkModel.title.ilike("%" + search + "%"),
                BookmarkModel.description.ilike("%" + search + "%")
            )
        )
    if tag:
        bookmarks = bookmarks.filter(BookmarkModel.tags.any(TagModel.title.ilike(tag)))
    if saved_before:
        bookmarks = bookmarks.filter(BookmarkModel.timestamp < saved_before)
    if saved_after:
        bookmarks = bookmarks.filter(BookmarkModel.timestamp > saved_after)
    total_count = bookmarks.count()
    if sort_by:
        if sort_by == SortBy.tags:
            bookmarks = bookmarks.outerjoin(BookmarkModel.tags)
            sort_column = TagModel.title
        else:
            sort_column = getattr(BookmarkModel, sort_by.value)
        if order_by == OrderBy.ascending:
            bookmarks = bookmarks.order_by(sort_column.asc())
        else:
            bookmarks = bookmarks.order_by(sort_column.desc())
    bookmarks = bookmarks.limit(limit)
    bookmarks = bookmarks.offset(offset)
    return {
        "total_count": total_count,
        "bookmarks": bookmarks.all()
    }

"""
  Steps to build this endpoint:
                               
  1. Define all optional parameters in the function signature
  2. Start with a base query: query = db.query(BookmarkModel)                                                                                        
  3. For each parameter — check if it's not None, then chain a .filter() onto query
  4. Handle sort_by and order separately using .order_by()                                                                                           
  5. Apply limit and offset last for pagination                                                                                                      
  6. Run .all() to get results                                                                                                                       
  7. Return results + total count                                                                                                                    
                                                                                                                                                     
  The key insight is that SQLAlchemy queries are lazy — you can keep chaining .filter() calls before executing. You only hit the DB when you call    
  .all() or .first().
"""


# SEARCH by title (returns list of matches)
@app.get("/bookmarks/search/{bookmark_title}", response_model=List[Bookmark])
def search_bookmarks_by_title(bookmark_title: str, db: Session = Depends(get_db)):
    bookmarks = db.query(BookmarkModel).filter(BookmarkModel.title.contains(bookmark_title)).all()
    return bookmarks

@app.get("/bookmarks/{bookmark_id}", response_model = Bookmark)
def read_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
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

@app.post("/bookmarks/{bookmark_id}/tags", response_model = Bookmark)
def add_tags(bookmark_id: int, tags : List[TagBase], db: Session = Depends(get_db)):
    db_bookmark = db.query(BookmarkModel).filter(BookmarkModel.id == bookmark_id).first()
    if not db_bookmark:
        raise HTTPException(status_code=404, detail="bookmark not found")
    for tag in tags:
        db_tag = db.query(TagModel).filter(TagModel.title == tag.title).first()
        if not db_tag:
            db_tag = TagModel(**tag.model_dump())
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
        tagConnected = False
        for dbtag in db_bookmark.tags: 
            if dbtag.id == db_tag.id:
                tagConnected = True
        if tagConnected:
            continue
        db_bookmark.tags.append(db_tag)
        db.commit()
        db.refresh(db_bookmark)
    
    return db_bookmark

# get all tags
@app.get("/tags", response_model=List[Tag])
def get_tags(db: Session = Depends(get_db)):
    tags = db.query(TagModel).all()
    return tags

@app.delete("/bookmarks/{bookmark_id}/tags/{tag_id}", response_model=Bookmark)
def delete_tag(bookmark_id : int, tag_id : int, db: Session = Depends(get_db)):
    db_bookmark = db.query(BookmarkModel).filter(BookmarkModel.id == bookmark_id).first()
    if not db_bookmark:
        raise HTTPException(status_code=404, detail="bookmark not found")
    for dbtag in db_bookmark.tags: 
        if dbtag.id == tag_id:
            db_bookmark.tags.remove(dbtag)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark


        









