import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import streamlit as st
from supabase import create_client, Client

class SessionManager:
    """
    Manages session state, conversation history, and persistence using Supabase.
    Handles loading/saving chat sessions with readable identifiers.
    """
    
    def __init__(self):
        """Initialize SessionManager with Supabase client or fallback to local storage."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.local_cache_dir = "session_cache"
        
        # Initialize Supabase client if credentials available
        self.supabase: Optional[Client] = None
        if self.supabase_url and self.supabase_key:
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                st.warning(f"Supabase connection failed: {e}. Using local cache.")
        
        # Create local cache directory if it doesn't exist
        if not os.path.exists(self.local_cache_dir):
            os.makedirs(self.local_cache_dir)
    
    def initialize_session(self) -> None:
        """Initialize session state with default values if not already set."""
        defaults = {
            "messages": [],
            "session_id": self._generate_session_id(),
            "user_name": "User",
            "model_selection": "gpt-4o-mini",
            "api_keys": {},
            "uploaded_files": [],
            "conversation_history": [],
            "current_conversation": None,
            "temperature": 0.7,
            "max_tokens": 2000,
            "system_prompt": "You are a helpful AI assistant.",
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def _generate_session_id(self) -> str:
        """Generate a readable session identifier with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"
    
    def save_session(self, session_name: Optional[str] = None) -> bool:
        """
        Save current session state to Supabase or local cache.
        
        Args:
            session_name: Optional custom name for the session
            
        Returns:
            bool: True if save was successful
        """
        session_data = {
            "session_id": st.session_state.get("session_id"),
            "session_name": session_name or st.session_state.get("session_id"),
            "messages": st.session_state.get("messages", []),
            "model_selection": st.session_state.get("model_selection"),
            "user_name": st.session_state.get("user_name"),
            "uploaded_files": st.session_state.get("uploaded_files", []),
            "temperature": st.session_state.get("temperature"),
            "max_tokens": st.session_state.get("max_tokens"),
            "system_prompt": st.session_state.get("system_prompt"),
            "timestamp": datetime.now().isoformat(),
        }
        
        # Try Supabase first
        if self.supabase:
            try:
                response = self.supabase.table("sessions").upsert(session_data).execute()
                return True
            except Exception as e:
                st.warning(f"Supabase save failed: {e}. Saving locally.")
        
        # Fallback to local storage
        return self._save_local(session_data)
    
    def _save_local(self, session_data: Dict[str, Any]) -> bool:
        """Save session data to local JSON file."""
        try:
            file_path = os.path.join(
                self.local_cache_dir, 
                f"{session_data['session_id']}.json"
            )
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Local save failed: {e}")
            return False
    
    def load_session(self, session_id: str) -> bool:
        """
        Load a session from Supabase or local cache.
        
        Args:
            session_id: The session identifier to load
            
        Returns:
            bool: True if load was successful
        """
        session_data = None
        
        # Try Supabase first
        if self.supabase:
            try:
                response = self.supabase.table("sessions")\
                    .select("*")\
                    .eq("session_id", session_id)\
                    .execute()
                if response.data:
                    session_data = response.data[0]
            except Exception as e:
                st.warning(f"Supabase load failed: {e}. Trying local cache.")
        
        # Fallback to local storage
        if not session_data:
            session_data = self._load_local(session_id)
        
        if session_data:
            self._restore_session_state(session_data)
            return True
        
        return False
    
    def _load_local(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from local JSON file."""
        try:
            file_path = os.path.join(self.local_cache_dir, f"{session_id}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"Local load failed: {e}")
        return None
    
    def _restore_session_state(self, session_data: Dict[str, Any]) -> None:
        """Restore session state from loaded data."""
        st.session_state.update({
            "messages": session_data.get("messages", []),
            "session_id": session_data.get("session_id"),
            "model_selection": session_data.get("model_selection", "gpt-4o-mini"),
            "user_name": session_data.get("user_name", "User"),
            "uploaded_files": session_data.get("uploaded_files", []),
            "temperature": session_data.get("temperature", 0.7),
            "max_tokens": session_data.get("max_tokens", 2000),
            "system_prompt": session_data.get("system_prompt", "You are a helpful AI assistant."),
        })
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Retrieve all available sessions.
        
        Returns:
            List of session metadata (id, name, timestamp)
        """
        sessions = []
        
        # Try Supabase first
        if self.supabase:
            try:
                response = self.supabase.table("sessions")\
                    .select("session_id, session_name, timestamp")\
                    .order("timestamp", desc=True)\
                    .execute()
                sessions = response.data
                return sessions
            except Exception as e:
                st.warning(f"Supabase query failed: {e}. Using local cache.")
        
        # Fallback to local storage
        sessions = self._get_local_sessions()
        return sessions
    
    def _get_local_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions from local cache."""
        sessions = []
        try:
            for filename in os.listdir(self.local_cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.local_cache_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        sessions.append({
                            "session_id": data.get("session_id"),
                            "session_name": data.get("session_name"),
                            "timestamp": data.get("timestamp")
                        })
            # Sort by timestamp descending
            sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        except Exception as e:
            st.error(f"Error reading local sessions: {e}")
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from storage.
        
        Args:
            session_id: The session to delete
            
        Returns:
            bool: True if deletion was successful
        """
        success = False
        
        # Delete from Supabase
        if self.supabase:
            try:
                self.supabase.table("sessions").delete().eq("session_id", session_id).execute()
                success = True
            except Exception as e:
                st.warning(f"Supabase delete failed: {e}")
        
        # Delete from local storage
        try:
            file_path = os.path.join(self.local_cache_dir, f"{session_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                success = True
        except Exception as e:
            st.error(f"Local delete failed: {e}")
        
        return success
    
    def clear_current_session(self) -> None:
        """Clear current session and start fresh."""
        st.session_state.messages = []
        st.session_state.session_id = self._generate_session_id()
        st.session_state.uploaded_files = []
    
    def auto_save(self) -> None:
        """Auto-save current session (call this after important state changes)."""
        if len(st.session_state.get("messages", [])) > 0:
            self.save_session()

    def get_chat_history(self) -> List[Dict[str, Any]]:
        """
        Get chat history for the current session.
        
        Returns:
            List of message dictionaries
        """
        return st.session_state.get("messages", [])
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the current session.
        
        Args:
            role: The role (user/assistant)
            content: The message content
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append(message)
        self.auto_save()