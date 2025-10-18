"""
Database handler for chat history management.
Provides simple interface for saving and loading chat data using the ChatHistoryDAO.
"""
from typing import List, Dict, Optional
from database.chat_history_dao import ChatHistoryDAO
import os

# Initialize the DAO with a default database path
DB_PATH = os.getenv("SQLITE_DB_PATH", "chat_history.db")
chat_dao = ChatHistoryDAO(db_path=DB_PATH)


def save_chat(chat_data: Dict) -> None:
    """
    Save a chat message to the database.
    
    Args:
        chat_data: Dictionary containing:
            - user_id: Unique identifier for the user (used as session_id)
            - message: User's message
            - response: Assistant's response
            - timestamp: ISO timestamp string
    """
    user_id = chat_data.get("user_id", "default_session")
    message = chat_data.get("message", "")
    response = chat_data.get("response", "")
    
    # Save user message
    if message:
        chat_dao.save_message(
            session_id=user_id,
            message_role="user",
            content=message
        )
    
    # Save assistant response
    if response:
        chat_dao.save_message(
            session_id=user_id,
            message_role="assistant",
            content=response
        )


def load_chat(user_id: str, limit: Optional[int] = 50) -> List[Dict]:
    """
    Load chat history for a specific user.
    
    Args:
        user_id: Unique identifier for the user (used as session_id)
        limit: Maximum number of messages to retrieve
    
    Returns:
        List of chat messages
    """
    return chat_dao.get_chat_history(session_id=user_id, limit=limit)


def delete_chat_history(user_id: str) -> int:
    """
    Delete all chat history for a specific user.
    
    Args:
        user_id: Unique identifier for the user (used as session_id)
    
    Returns:
        Number of messages deleted
    """
    return chat_dao.clear_session(session_id=user_id)


def get_recent_context(user_id: str, num_messages: int = 10) -> List[Dict]:
    """
    Get recent conversation context for a user.
    
    Args:
        user_id: Unique identifier for the user
        num_messages: Number of recent messages to retrieve
    
    Returns:
        List of recent messages
    """
    return chat_dao.get_recent_context(session_id=user_id, num_messages=num_messages)
