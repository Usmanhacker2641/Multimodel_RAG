import streamlit as st
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

"""
History Persistence Module
Handles saving and loading conversation history through FastAPI backend.
Provides seamless chat session management with clean UI integration.
"""



class HistoryPersistence:
    """Manages conversation history persistence with backend integration."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize history persistence manager.
        
        Args:
            base_url: Base URL of the FastAPI backend
        """
        self.base_url = base_url.rstrip('/')
        self.save_endpoint = f"{self.base_url}/api/chat/save"
        self.load_endpoint = f"{self.base_url}/api/chat/load"
        self.list_endpoint = f"{self.base_url}/api/chat/history"
        self.delete_endpoint = f"{self.base_url}/api/chat/delete"
        self.rename_endpoint = f"{self.base_url}/api/chat/rename"
    
    def save_chat(
        self,
        session_id: str,
        history: List[Dict[str, Any]],
        api_key: str,
        session_name: Optional[str] = None
    ) -> bool:
        """
        Save chat history to backend.
        
        Args:
            session_id: Unique session identifier
            history: List of message dictionaries
            api_key: User's API key for authentication
            session_name: Optional custom name for the session
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            payload = {
                "session_id": session_id,
                "history": history,
                "session_name": session_name or f"Chat - {datetime.now().strftime('%b %d, %Y %H:%M')}",
                "timestamp": datetime.now().isoformat()
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.save_endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self._show_save_indicator(success=True)
                return True
            else:
                self._show_save_indicator(success=False)
                return False
                
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Failed to save chat: {str(e)}")
            return False
    
    def load_chat(self, session_id: str, api_key: str) -> Optional[List[Dict[str, Any]]]:
        """
        Load chat history from backend.
        
        Args:
            session_id: Unique session identifier
            api_key: User's API key for authentication
            
        Returns:
            List of message dictionaries or None if failed
        """
        try:
            with st.spinner("Retrieving your previous session..."):
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                params = {"session_id": session_id}
                
                response = requests.get(
                    self.load_endpoint,
                    params=params,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("history", [])
                else:
                    st.warning("⚠️ Could not load chat history")
                    return None
                    
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Failed to load chat: {str(e)}")
            return None
    
    def list_sessions(self, api_key: str) -> Optional[List[Dict[str, Any]]]:
        """
        List all chat sessions for the user.
        
        Args:
            api_key: User's API key for authentication
            
        Returns:
            List of session metadata or None if failed
        """
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                self.list_endpoint,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("sessions", [])
            else:
                return []
                
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Failed to load session list: {str(e)}")
            return []
    
    def delete_session(self, session_id: str, api_key: str) -> bool:
        """
        Delete a chat session.
        
        Args:
            session_id: Unique session identifier
            api_key: User's API key for authentication
            
        Returns:
            bool: True if deletion successful
        """
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.delete(
                f"{self.delete_endpoint}/{session_id}",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Failed to delete session: {str(e)}")
            return False
    
    def rename_session(self, session_id: str, new_name: str, api_key: str) -> bool:
        """
        Rename a chat session.
        
        Args:
            session_id: Unique session identifier
            new_name: New name for the session
            api_key: User's API key for authentication
            
        Returns:
            bool: True if rename successful
        """
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "session_id": session_id,
                "new_name": new_name
            }
            
            response = requests.put(
                self.rename_endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Failed to rename session: {str(e)}")
            return False
    
    def _show_save_indicator(self, success: bool = True):
        """Display subtle save indicator."""
        if success:
            if 'last_save_time' not in st.session_state:
                st.session_state.last_save_time = datetime.now()
        else:
            st.toast("⚠️ Auto-save failed", icon="⚠️")
    
    def render_history_sidebar(self, api_key: str, on_load_callback=None):
        """
        Render chat history sidebar UI.
        
        Args:
            api_key: User's API key
            on_load_callback: Function to call when loading a session
        """
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📜 Chat History")
        
        if not api_key:
            st.sidebar.info("Enter your API key to view history")
            return
        
        sessions = self.list_sessions(api_key)
        
        if not sessions:
            st.sidebar.info("No saved conversations yet")
            return
        
        for session in sessions:
            col1, col2, col3 = st.sidebar.columns([3, 1, 1])
            
            with col1:
                if st.button(
                    session.get('name', 'Untitled Chat'),
                    key=f"load_{session['id']}",
                    use_container_width=True
                ):
                    if on_load_callback:
                        on_load_callback(session['id'])
            
            with col2:
                if st.button("✏️", key=f"rename_{session['id']}"):
                    st.session_state[f"rename_modal_{session['id']}"] = True
            
            with col3:
                if st.button("🗑️", key=f"delete_{session['id']}"):
                    if self.delete_session(session['id'], api_key):
                        st.success("Session deleted")
                        st.rerun()
            
            # Rename modal
            if st.session_state.get(f"rename_modal_{session['id']}", False):
                new_name = st.sidebar.text_input(
                    "New name:",
                    value=session.get('name', ''),
                    key=f"input_rename_{session['id']}"
                )
                
                col_confirm, col_cancel = st.sidebar.columns(2)
                with col_confirm:
                    if st.button("✓", key=f"confirm_{session['id']}"):
                        if self.rename_session(session['id'], new_name, api_key):
                            st.success("Renamed!")
                            st.session_state[f"rename_modal_{session['id']}"] = False
                            st.rerun()
                
                with col_cancel:
                    if st.button("✗", key=f"cancel_{session['id']}"):
                        st.session_state[f"rename_modal_{session['id']}"] = False
                        st.rerun()
            
            st.sidebar.markdown(
                f"<small style='color: #888;'>{session.get('timestamp', '')}</small>",
                unsafe_allow_html=True
            )
        
        # New chat button
        st.sidebar.markdown("---")
        if st.sidebar.button("➕ New Chat", use_container_width=True):
            if 'messages' in st.session_state:
                st.session_state.messages = []
            if 'session_id' in st.session_state:
                st.session_state.session_id = None
            st.rerun()


# Utility functions for easy integration
def auto_save_message(
    message: Dict[str, Any],
    persistence_manager: HistoryPersistence,
    session_id: str,
    api_key: str
):
    """
    Auto-save a new message to history.
    
    Args:
        message: Message dictionary to save
        persistence_manager: HistoryPersistence instance
        session_id: Current session ID
        api_key: User's API key
    """
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    st.session_state.messages.append(message)
    
    # Auto-save with debouncing
    persistence_manager.save_chat(
        session_id=session_id,
        history=st.session_state.messages,
        api_key=api_key
    )


def initialize_history(api_key: str) -> HistoryPersistence:
    """
    Initialize history persistence manager.
    
    Args:
        api_key: User's API key
        
    Returns:
        HistoryPersistence instance
    """
    if 'history_manager' not in st.session_state:
        st.session_state.history_manager = HistoryPersistence()
    
    return st.session_state.history_manager