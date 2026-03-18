from pydantic import BaseModel, Field
from datetime import datetime


class BookmarkBase(BaseModel):
    title: str
    url: str
    description: str | None = None
    timestamp: str | datetime = Field(datetime=datetime.now)

class BookmarkCreate(BookmarkBase):
    pass

class Bookmark(BookmarkBase):
    id : int
    class config:
        orm = True

