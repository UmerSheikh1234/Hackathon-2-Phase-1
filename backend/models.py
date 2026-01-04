from typing import Optional, List
from datetime import datetime, timezone 
from sqlmodel import Field, SQLModel, Relationship

class User(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), nullable=False)
    
    conversations: List["Conversation"] = Relationship(back_populates="user")

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    completed: bool = Field(default=False)
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), nullable=False)
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), nullable=False)

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: int
    completed: bool

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), nullable=False)
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), nullable=False)
    
    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str # "user" or "assistant"
    content: str
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), nullable=False)

    conversation: Conversation = Relationship(back_populates="messages")