import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import CORS
from dotenv import load_dotenv

from db import engine, create_db_and_tables
from routes import tasks, chat


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
    "https://hackathon-2-phase-1-5eis.vercel.app", # Your Vercel deployment URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])


@app.get("/")
async def read_root():
    return {"message": "Todo FastAPI Backend is running!"}