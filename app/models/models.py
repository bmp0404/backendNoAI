from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import os
from pathlib import Path

current_dir = Path(__file__).resolve().parent
env_path = current_dir.parent / ".env"
load_dotenv(env_path)

print('hellohellohello')
print(env_path)
print(os.getenv("DB_PORT"))


DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

bookmarktag = Table(
    "bookmarktag",
    Base.metadata,
    Column("bookmark_id", ForeignKey("bookmark.id")),
    Column("tag_id", ForeignKey("tag.id")),
)

class Bookmark(Base):
    __tablename__ = "bookmark"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    tags = relationship("Tag", secondary=bookmarktag)

class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    bookmarks = relationship("Bookmark", secondary=bookmarktag)

