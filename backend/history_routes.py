from fastapi import APIRouter, Form, HTTPException
from typing import List, Dict, Optional
from datetime import datetime
from services.db_handler import save_chat, load_chat, delete_chat_history
from core.logger import setup_logger

logger = setup_logger("backend.history")
router = APIRouter(prefix="/history", tags=["History"])

@router.post("/save")
async def save_history(
    user_id: str = Form(...), 
    message: str = Form(...), 
    response: str = Form(...)
):
    """
    Save a chat message and its response to the database.
    
    Args:
        user_id: Unique identifier for the user
        message: User's query/message
        response: Model's response to the query
    
    Returns:
        Status confirmation with timestamp
    """
    try:
        logger.info("Saving chat history: user_id=%s message_length=%d", user_id, len(message))
        timestamp = datetime.now().isoformat()
        chat_data = {
            "user_id": user_id,
            "message": message,
            "response": response,
            "timestamp": timestamp
        }
        save_chat(chat_data)
        logger.info("Chat history saved successfully: user_id=%s", user_id)
        return {
            "status": "success",
            "message": "Chat saved successfully",
            "timestamp": timestamp
        }
    except Exception as e:
        logger.exception("Failed to save chat history: user_id=%s error=%s", user_id, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to save chat: {str(e)}")


@router.get("/load/{user_id}")
async def load_history(user_id: str, limit: Optional[int] = 50):
    """
    Load chat history for a specific user.
    
    Args:
        user_id: Unique identifier for the user
        limit: Maximum number of messages to retrieve (default: 50)
    
    Returns:
        List of chat messages with timestamps
    """
    try:
        logger.info("Loading chat history: user_id=%s limit=%d", user_id, limit)
        history = load_chat(user_id, limit)
        logger.info("Chat history loaded: user_id=%s count=%d", user_id, len(history))
        return {
            "status": "success",
            "user_id": user_id,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        logger.exception("Failed to load chat history: user_id=%s error=%s", user_id, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to load chat history: {str(e)}")


@router.delete("/delete/{user_id}")
async def delete_history(user_id: str):
    """
    Delete all chat history for a specific user.
    
    Args:
        user_id: Unique identifier for the user
    
    Returns:
        Confirmation of deletion
    """
    try:
        logger.info("Deleting chat history: user_id=%s", user_id)
        delete_chat_history(user_id)
        logger.info("Chat history deleted successfully: user_id=%s", user_id)
        return {
            "status": "success",
            "message": f"Chat history deleted for user {user_id}"
        }
    except Exception as e:
        logger.exception("Failed to delete chat history: user_id=%s error=%s", user_id, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete chat history: {str(e)}")


@router.get("/recent/{user_id}")
async def get_recent_chats(user_id: str, count: int = 10):
    """
    Get the most recent chat messages for a user.
    
    Args:
        user_id: Unique identifier for the user
        count: Number of recent messages to retrieve (default: 10)
    
    Returns:
        Recent chat messages
    """
    try:
        history = load_chat(user_id, count)
        return {
            "status": "success",
            "user_id": user_id,
            "recent_chats": history[-count:] if len(history) > count else history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve recent chats: {str(e)}")