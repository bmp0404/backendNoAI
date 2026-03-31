from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class BookmarkBase(BaseModel):
    title: str
    url: HttpUrl
    description: str | None = None
    timestamp: str | datetime = Field(default=datetime.now())

class BookmarkCreate(BookmarkBase):
    pass

class Bookmark(BookmarkBase):
    id : int
    class config:
        orm = True

