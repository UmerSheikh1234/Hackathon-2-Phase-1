import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv

from db import engine, create_db_and_tables
from routes import tasks

load_dotenv() # Load environment variables from .env file

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(tasks.router, prefix="/api")

@app.get("/")
async def read_root():
    return {"message": "Todo FastAPI Backend is running!"}