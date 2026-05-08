import pytest
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / "app" / ".env")

DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

@pytest.fixture(scope="session", autouse=True)
def reset_db():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE bookmarktag, tag, bookmark RESTART IDENTITY CASCADE;"))
        conn.commit()
    yield
    engine.dispose()
