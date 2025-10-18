import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
import time

class ChatUI:
    """Professional chat interface component with message history and user interaction."""
    
    def __init__(self, session_manager):
        """
        Initialize ChatUI with session manager.
        
        Args:
            session_manager: Session manager instance for storing chat history
        """
        self.session_manager = session_manager
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables for chat."""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'is_thinking' not in st.session_state:
            st.session_state.is_thinking = False
    
    def _format_timestamp(self, timestamp: Optional[datetime] = None) -> str:
        """Format timestamp for display."""
        if timestamp is None:
            timestamp = datetime.now()
        return timestamp.strftime("%I:%M %p")
    
    def display_message(self, role: str, content: str, metadata: Optional[Dict] = None, 
                       timestamp: Optional[datetime] = None):
        """
        Display a single chat message with styling.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (sources, confidence, etc.)
            timestamp: Message timestamp
        """
        avatar = "🧑‍💼" if role == "user" else "🤖"
        
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)
            
            # Display timestamp
            if timestamp:
                st.caption(f"🕒 {self._format_timestamp(timestamp)}")
            
            # Display metadata if available
            if metadata:
                with st.expander("📋 View Details"):
                    if 'sources' in metadata:
                        st.markdown("**Sources:**")
                        for idx, source in enumerate(metadata['sources'], 1):
                            st.markdown(f"{idx}. {source}")
                    
                    if 'confidence' in metadata:
                        st.markdown(f"**Confidence:** {metadata['confidence']:.2%}")
                    
                    if 'model' in metadata:
                        st.markdown(f"**Model:** {metadata['model']}")
    
    def display_thinking_animation(self):
        """Display AI thinking animation."""
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🧠 Thinking..."):
                time.sleep(0.5)  # Brief pause for visual effect
    
    def load_chat_history(self):
        """Load and display chat history from session manager."""
        history = self.session_manager.get_chat_history()
        
        if history:
            for message in history:
                self.display_message(
                    role=message.get('role', 'user'),
                    content=message.get('content', ''),
                    metadata=message.get('metadata'),
                    timestamp=message.get('timestamp')
                )
        else:
            # Welcome message
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown("👋 Hello! I'm your AI assistant. How can I help you today?")
    
    def save_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Save message to session state and session manager.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now(),
            'metadata': metadata
        }
        
        st.session_state.messages.append(message)
        self.session_manager.add_message(message)
    
    def render(self) -> Optional[str]:
        """
        Render the complete chat interface.
        
        Returns:
            User input if submitted, None otherwise
        """
        # Header
        st.title("💬 Chat Interface")
        st.markdown("---")
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            self.load_chat_history()
            
            # Display current session messages
            for message in st.session_state.messages:
                self.display_message(
                    role=message['role'],
                    content=message['content'],
                    metadata=message.get('metadata'),
                    timestamp=message.get('timestamp')
                )
            
            # Show thinking animation if processing
            if st.session_state.is_thinking:
                self.display_thinking_animation()
        
        # Input area at the bottom
        st.markdown("---")
        
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_input(
                "Your message",
                key="user_input",
                placeholder="Type your message here...",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.button("🚀 Send", use_container_width=True)
        
        # Handle message submission
        if send_button and user_input.strip():
            return user_input.strip()
        
        return None
    
    def clear_chat(self):
        """Clear chat history."""
        st.session_state.messages = []
        self.session_manager.clear_history()
        st.rerun()


def create_chat_ui(session_manager) -> ChatUI:
    """
    Factory function to create ChatUI instance.
    
    Args:
        session_manager: Session manager instance
        
    Returns:
        ChatUI instance
    """
    return ChatUI(session_manager)


# Sidebar controls
def render_sidebar_controls(chat_ui: ChatUI):
    """Render sidebar controls for chat interface."""
    with st.sidebar:
        st.markdown("### ⚙️ Chat Controls")
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            chat_ui.clear_chat()
        
        st.markdown("---")
        
        # Settings
        with st.expander("🎨 Display Settings"):
            show_timestamps = st.checkbox("Show timestamps", value=True)
            show_metadata = st.checkbox("Show message details", value=True)
            
        with st.expander("📊 Statistics"):
            st.metric("Messages", len(st.session_state.get('messages', [])))
            st.metric("Session Duration", "Active")