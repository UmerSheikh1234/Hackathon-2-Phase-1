from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from db import get_session
from models import Task

router = APIRouter()

@router.post("/tasks/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task: Task, session: Session = Depends(get_session)):
    # In a real app, user_id would come from authentication
    # For now, let's assume a default user_id or get it from a header/query param
    # For simplicity, let's hardcode a user_id for now, or ensure task.user_id is provided
    # The spec assumes a user_id from auth: user_id: str = Field(index=True, foreign_key="user.id")
    # For Phase 2, we're not implementing full auth yet, but need a user_id
    # Let's make user_id a required field in the request body for now, or default it
    # We will assume a user_id of "test_user" for now, which will be replaced by auth later.
    task.user_id = "test_user" # Placeholder until Better Auth is integrated
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/tasks/", response_model=List[Task])
async def read_tasks(
    session: Session = Depends(get_session),
    status_filter: Optional[str] = None, # "all", "pending", "completed"
    user_id: str = "test_user" # Placeholder for authenticated user
):
    query = select(Task).where(Task.user_id == user_id)
    if status_filter == "pending":
        query = query.where(Task.completed == False)
    elif status_filter == "completed":
        query = query.where(Task.completed == True)
    
    tasks = session.exec(query).all()
    return tasks

@router.get("/tasks/{task_id}", response_model=Task)
async def read_task(task_id: int, session: Session = Depends(get_session), user_id: str = "test_user"):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: Task, session: Session = Depends(get_session), user_id: str = "test_user"):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update only provided fields
    task.title = task_update.title if task_update.title is not None else task.title
    task.description = task_update.description if task_update.description is not None else task.description
    task.completed = task_update.completed if task_update.completed is not None else task.completed
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, session: Session = Depends(get_session), user_id: str = "test_user"):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return

@router.patch("/tasks/{task_id}/complete", response_model=Task)
async def complete_task(task_id: int, session: Session = Depends(get_session), user_id: str = "test_user"):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.completed = True
    session.add(task)
    session.commit()
    session.refresh(task)
    return task