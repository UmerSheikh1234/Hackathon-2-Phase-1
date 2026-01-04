import os
from typing import Generator

from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Check if DATABASE_URL is set, otherwise use a default SQLite for development/testing
if not DATABASE_URL:
    print("DATABASE_URL not found in .env, using SQLite for local development.")
    # For a real project, this should be a proper development database
    engine = create_engine("sqlite:///./database.db")
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session