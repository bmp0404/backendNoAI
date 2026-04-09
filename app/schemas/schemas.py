from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime
from typing import List


class BookmarkBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    url: HttpUrl
    description: str | None = None
    timestamp: str | datetime = Field(default=datetime.now())
    tags: list[Tag]

class BookmarkCreate(BookmarkBase):
    pass

class Bookmark(BookmarkBase):
    id : int
    class config:
        orm = True

class BookmarkList(BaseModel):                                                                                                                            
  total_count: int
  bookmarks: List[Bookmark]

class TagBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title : str

class Tag(TagBase):
    id: int
    class config:
        orm = True




