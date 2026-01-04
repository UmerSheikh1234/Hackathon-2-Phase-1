from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session
from ..db import get_session

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int

router = APIRouter()

@router.post("/chat/", response_model=ChatResponse)
async def handle_chat(chat_request: ChatRequest, session: Session = Depends(get_session)):
    # For now, we'll just echo the message back.
    # In the full implementation, this is where we will:
    # 1. Load conversation history.
    # 2. Call the AI agent.
    # 3. Save the new messages.
    # 4. Return the AI's response.
    
    # Dummy logic for now:
    user_message = chat_request.message
    conversation_id = chat_request.conversation_id or 1 # Dummy conversation ID
    
    # Echo response
    ai_response = f"You said: '{user_message}'"
    
    return ChatResponse(response=ai_response, conversation_id=conversation_id)
