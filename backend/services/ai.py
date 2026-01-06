import os
from typing import List, Dict, Union
from openai import OpenAI
from dotenv import load_dotenv
from sqlmodel import Session, select
import json # Import json module

from ..models import Task, TaskCreate
from ..db import get_session

load_dotenv()

# Initialize OpenAI Client
# For local development, load OPENAI_API_KEY from .env
# For production, it should be set as an environment variable
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- AI Tools Definition ---
# These functions will be called by the AI agent based on user's natural language.

def get_tasks_tool(session: Session, status: str = "all", user_id: str = "test_user") -> List[Dict]:
    """
    Retrieves a list of tasks for the specified user.
    Can filter by status: 'all', 'pending', or 'completed'.
    """
    query = select(Task).where(Task.user_id == user_id)
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)
    
    tasks = session.exec(query).all()
    # Convert Task objects to dictionaries for tool output
    return [{"id": task.id, "title": task.title, "description": task.description, "completed": task.completed} for task in tasks]

def create_task_tool(session: Session, title: str, description: str = "", user_id: str = "test_user") -> Dict:
    """
    Creates a new task for the user with a given title and optional description.
    """
    new_task = Task(title=title, description=description, user_id=user_id)
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return {"id": new_task.id, "title": new_task.title, "description": new_task.description, "completed": new_task.completed}

def mark_task_complete_tool(session: Session, task_id: int, user_id: str = "test_user") -> Dict:
    """
    Marks an existing task as completed.
    """
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        return {"error": f"Task with ID {task_id} not found."}
    task.completed = True
    session.add(task)
    session.commit()
    session.refresh(task)
    return {"id": task.id, "title": task.title, "completed": task.completed}

def delete_task_tool(session: Session, task_id: int, user_id: str = "test_user") -> Dict:
    """
    Deletes an existing task.
    """
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        return {"error": f"Task with ID {task_id} not found."}
    session.delete(task)
    session.commit()
    return {"status": f"Task with ID {task_id} deleted successfully."}

# Map tool names to their corresponding functions
available_tools = {
    "get_tasks_tool": get_tasks_tool,
    "create_task_tool": create_task_tool,
    "mark_task_complete_tool": mark_task_complete_tool,
    "delete_task_tool": delete_task_tool,
}

# --- OpenAI Tool Definitions (for the API call) ---
# These are the schema descriptions for OpenAI to understand what tools are available.

openai_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_tasks_tool",
            "description": "Retrieves a list of tasks for the specified user. Can filter by status: 'all', 'pending', or 'completed'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status: 'all', 'pending', or 'completed'. Defaults to 'all'."
                    },
                    "user_id": {
                        "type": "string",
                        "description": "The ID of the user whose tasks to retrieve."
                    }
                },
                "required": ["user_id"] # User ID will be passed by the server
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_task_tool",
            "description": "Creates a new task for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task."
                    },
                    "description": {
                        "type": "string",
                        "description": "An optional description for the task."
                    },
                    "user_id": {
                        "type": "string",
                        "description": "The ID of the user for whom to create the task."
                    }
                },
                "required": ["title", "user_id"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mark_task_complete_tool",
            "description": "Marks an existing task as completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to mark as complete."
                    },
                    "user_id": {
                        "type": "string",
                        "description": "The ID of the user whose task to mark complete."
                    }
                },
                "required": ["task_id", "user_id"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task_tool",
            "description": "Deletes an existing task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete."
                    },
                    "user_id": {
                        "type": "string",
                        "description": "The ID of the user whose task to delete."
                    }
                },
                "required": ["task_id", "user_id"]
            },
        },
    },
]

# --- Main AI Chat Function ---

async def get_ai_response(user_message: str, conversation_messages: List[Dict], session: Session, user_id: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant for managing todo tasks. You have access to tools to create, view, mark complete, and delete tasks. Always respond in a helpful and concise manner. If asked to mark a task complete or delete a task, first confirm the task exists by listing tasks if you are unsure of the ID."},
        *conversation_messages, # Previous messages in the conversation
        {"role": "user", "content": user_message}
    ]

    response = openai_client.chat.completions.create(
        model="gpt-4", # Using a powerful model for function calling
        messages=messages,
        tools=openai_tools,
        tool_choice="auto", # Let the model decide whether to call a tool or respond
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        # Step 2: check if the model wanted to call a tool
        # Step 3: call the tool
        # Note: the JSON response may not always be valid; be sure to handle errors
        
        # Extend conversation with the assistant's reply (tool_calls)
        messages.append(response_message)
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_tools[function_name]
            function_args = tool_call.function.arguments
            
            # Inject user_id into tool arguments if not present (handled by tool definitions)
            if "user_id" not in function_args:
                function_args_dict = json.loads(function_args) # Parse to dict
                function_args_dict["user_id"] = user_id
                # Special handling for get_tasks_tool 'status' - default to 'all' if not provided
                if function_name == "get_tasks_tool" and "status" not in function_args_dict:
                    function_args_dict["status"] = "all"
                function_args = json.dumps(function_args_dict) # Convert back to string
            
            # Execute the tool function
            tool_response = function_to_call(session=session, **json.loads(function_args))
            
            # Extend conversation with tool output
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(tool_response),
                }
            )
        
        # Step 4: send the info for each tool call and tool response to the model
        second_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
        )
        return second_response.choices[0].message.content
    else:
        return response_message.content
