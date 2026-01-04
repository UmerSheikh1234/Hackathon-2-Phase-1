import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import CORS
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

# Add CORS middleware
origins = [
    "http://localhost:3000", # The origin for your frontend development server
    # You can add your Vercel deployment URL here later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

app.include_router(tasks.router, prefix="/api")

@app.get("/")
async def read_root():
    return {"message": "Todo FastAPI Backend is running!"}