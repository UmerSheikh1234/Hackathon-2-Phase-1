from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from ..db import get_session
from ..models import Task, TaskCreate

router = APIRouter()

@router.post("/tasks/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, session: Session = Depends(get_session)):
    # Create a new Task instance from the TaskCreate data
    task = Task.from_orm(task_data)
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
async def update_task(task_id: int, task_update: TaskCreate, session: Session = Depends(get_session), user_id: str = "test_user"):
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update only provided fields
    task_data = task_update.dict(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)
    
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