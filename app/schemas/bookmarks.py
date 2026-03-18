from pydantic import BaseModel, Field
from datetime import datetime

class Bookmark(BaseModel):
    title: str
    url: str
    description: str | None = None
    timestamp: str | datetime = Field(datetime=datetime.now)
