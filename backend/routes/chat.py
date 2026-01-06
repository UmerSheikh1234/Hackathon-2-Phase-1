from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from ..db import get_session
from ..models import Conversation, Message, User
from ..services.ai import get_ai_response # Import the AI response function

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int

router = APIRouter()

@router.post("/chat/", response_model=ChatResponse)
async def handle_chat(chat_request: ChatRequest, session: Session = Depends(get_session)):
    user_id = "test_user" # Hardcoded user_id for now

    # Ensure user exists (for conversation linking)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        user = User(id=user_id, email=f"{user_id}@example.com", name=user_id)
        session.add(user)
        session.commit()
        session.refresh(user)

    # Find or create conversation
    conversation = None
    if chat_request.conversation_id:
        conversation = session.exec(select(Conversation).where(Conversation.id == chat_request.conversation_id, Conversation.user_id == user_id)).first()
    
    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    
    # Store user message
    user_message_obj = Message(conversation_id=conversation.id, role="user", content=chat_request.message)
    session.add(user_message_obj)
    session.commit()
    session.refresh(user_message_obj)

    # Get conversation history
    conversation_messages = session.exec(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at)).all()
    # Format messages for OpenAI
    formatted_messages = [{"role": msg.role, "content": msg.content} for msg in conversation_messages]

    # Get AI response
    ai_response_content = await get_ai_response(
        user_message=chat_request.message,
        conversation_messages=formatted_messages,
        session=session,
        user_id=user_id # Pass user_id to AI tools
    )

    # Store AI response
    ai_message_obj = Message(conversation_id=conversation.id, role="assistant", content=ai_response_content)
    session.add(ai_message_obj)
    session.commit()
    session.refresh(ai_message_obj)

    return ChatResponse(response=ai_response_content, conversation_id=conversation.id)