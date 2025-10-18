import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

class ChatHistoryDAO:
    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_role TEXT NOT NULL,
                content TEXT NOT NULL,
                model TEXT,
                temperature REAL,
                category TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT)""")
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_session_id ON chat_history(session_id)""")
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history(timestamp)""")
        conn.commit()
        conn.close()
    
    def save_message(self, session_id: str, message_role: str, content: str, model: Optional[str] = None, temperature: Optional[float] = None, category: Optional[str] = None, metadata: Optional[Dict] = None) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None
        cursor.execute("""INSERT INTO chat_history (session_id, message_role, content, model, temperature, category, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)""", (session_id, message_role, content, model, temperature, category, metadata_json))
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_id
    
    def get_chat_history(self, session_id: str, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """SELECT id, session_id, message_role, content, model, temperature, category, timestamp, metadata FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC"""
        params = [session_id]
        if limit:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        cursor.execute(query, params)
        rows = cursor.fetchall()
        history = [{"id": r["id"], "session_id": r["session_id"], "message_role": r["message_role"], "content": r["content"], "model": r["model"], "temperature": r["temperature"], "category": r["category"], "timestamp": r["timestamp"], "metadata": json.loads(r["metadata"]) if r["metadata"] else None} for r in rows]
        conn.close()
        return history
    
    def get_recent_context(self, session_id: str, num_messages: int = 10) -> List[Dict]:
        return self.get_chat_history(session_id, limit=num_messages)
    
    def clear_session(self, session_id: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count
