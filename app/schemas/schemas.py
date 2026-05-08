from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator
from datetime import datetime
from typing import List

class TagBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title : str

class Tag(TagBase):
    id: int

class BookmarkBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    url: str  # stored as plain str, validated below
    # TODO(human): implement validate_url below
    description: str | None = None
    timestamp: str | datetime = Field(default=datetime.now())
    tags: list[Tag] = []

class BookmarkCreate(BookmarkBase):
    pass

class Bookmark(BookmarkBase):
    id: int

class BookmarkList(BaseModel):                                                                                                                            
  total_count: int
  bookmarks: List[Bookmark]






