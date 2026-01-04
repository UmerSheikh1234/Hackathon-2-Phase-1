from typing import Optional
from datetime import datetime, timezone 
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), nullable=False)

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key="user.id") # Link to User model
    title: str = Field(nullable=False)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), nullable=False)
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), nullable=False)

    # Optional: Pydantic configuration for better JSON representation
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
            }
        }