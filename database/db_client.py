import os
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import logging
from supabase import create_client, Client
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

from database.chat_history_dao import ChatHistoryDAO

"""
Universal Database Connector for Supabase or MongoDB Atlas
This module provides a unified interface for database operations across different database systems.
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types"""
    SUPABASE = "supabase"
    MONGODB = "mongodb"


class DatabaseClient:
    """
    Universal database client supporting Supabase and MongoDB Atlas.
    Acts as a bridge between the application and cloud databases.
    """
    
    def __init__(self, db_type: str, credentials: Dict[str, str]):
        """
        Initialize database connection.
        
        Args:
            db_type: Type of database ('supabase' or 'mongodb')
            credentials: Dictionary containing connection credentials
        """
        self.db_type = db_type.lower()
        self.credentials = self._sanitize_credentials(credentials)
        self.client = None
        self.db = None
        
        # Initialize connection
        self._connect()
    
    def _sanitize_credentials(self, credentials: Dict[str, str]) -> Dict[str, str]:
        """
        Sanitize and validate credentials to prevent injection attacks.
        
        Args:
            credentials: Raw credentials dictionary
            
        Returns:
            Sanitized credentials
        """
        sanitized = {}
        for key, value in credentials.items():
            if isinstance(value, str):
                # Remove potentially dangerous characters
                sanitized[key] = value.strip()
            else:
                sanitized[key] = value
        return sanitized
    
    def _connect(self):
        """Establish database connection based on type"""
        try:
            if self.db_type == DatabaseType.SUPABASE.value:
                self._connect_supabase()
            elif self.db_type == DatabaseType.MONGODB.value:
                self._connect_mongodb()
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            logger.info(f"Successfully connected to {self.db_type} database")
            
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise ConnectionError(f"Failed to connect to {self.db_type}: {str(e)}")
    
    def _connect_supabase(self):
        """Initialize Supabase connection"""
        try:
            
            url = self.credentials.get('supabase_url')
            key = self.credentials.get('supabase_key')
            
            if not url or not key:
                raise ValueError("Supabase URL and Key are required")
            
            self.client: Client = create_client(url, key)
            logger.info("Supabase client initialized")
            
        except ImportError:
            raise ImportError("Supabase library not installed. Install with: pip install supabase")
    
    def _connect_mongodb(self):
        """Initialize MongoDB Atlas connection"""
        try:
            
            uri = self.credentials.get('mongodb_uri')
            db_name = self.credentials.get('database_name', 'multimodel_rag')
            
            if not uri:
                raise ValueError("MongoDB URI is required")
            
            self.client = MongoClient(uri, server_api=ServerApi('1'))
            self.db = self.client[db_name]
            logger.info(f"MongoDB client initialized for database: {db_name}")
            
        except ImportError:
            raise ImportError("PyMongo library not installed. Install with: pip install pymongo")
    
    def validate_connection(self) -> bool:
        """
        Validate database connection with a simple operation.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            if self.db_type == DatabaseType.SUPABASE.value:
                # Try to fetch from a system table
                self.client.table('_realtime').select("*").limit(1).execute()
                return True
                
            elif self.db_type == DatabaseType.MONGODB.value:
                # Ping the database
                self.client.admin.command('ping')
                return True
                
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            return False
    
    def insert_one(self, collection: str, data: Dict[str, Any]) -> Optional[Any]:
        """
        Insert a single document/record.
        
        Args:
            collection: Table/collection name
            data: Data to insert
            
        Returns:
            Inserted document ID or result
        """
        try:
            if self.db_type == DatabaseType.SUPABASE.value:
                result = self.client.table(collection).insert(data).execute()
                return result.data[0] if result.data else None
                
            elif self.db_type == DatabaseType.MONGODB.value:
                result = self.db[collection].insert_one(data)
                return result.inserted_id
                
        except Exception as e:
            logger.error(f"Insert operation failed: {str(e)}")
            raise
    
    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document/record.
        
        Args:
            collection: Table/collection name
            query: Query filter
            
        Returns:
            Found document or None
        """
        try:
            if self.db_type == DatabaseType.SUPABASE.value:
                # Convert query dict to Supabase filter
                table = self.client.table(collection).select("*")
                for key, value in query.items():
                    table = table.eq(key, value)
                result = table.limit(1).execute()
                return result.data[0] if result.data else None
                
            elif self.db_type == DatabaseType.MONGODB.value:
                return self.db[collection].find_one(query)
                
        except Exception as e:
            logger.error(f"Find operation failed: {str(e)}")
            raise
    
    def find_many(self, collection: str, query: Dict[str, Any] = None, 
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find multiple documents/records.
        
        Args:
            collection: Table/collection name
            query: Query filter (optional)
            limit: Maximum number of results
            
        Returns:
            List of found documents
        """
        try:
            query = query or {}
            
            if self.db_type == DatabaseType.SUPABASE.value:
                table = self.client.table(collection).select("*")
                for key, value in query.items():
                    table = table.eq(key, value)
                result = table.limit(limit).execute()
                return result.data or []
                
            elif self.db_type == DatabaseType.MONGODB.value:
                return list(self.db[collection].find(query).limit(limit))
                
        except Exception as e:
            logger.error(f"Find many operation failed: {str(e)}")
            raise
    
    def update_one(self, collection: str, query: Dict[str, Any], 
                   update: Dict[str, Any]) -> bool:
        """
        Update a single document/record.
        
        Args:
            collection: Table/collection name
            query: Query filter to find document
            update: Update data
            
        Returns:
            True if update successful
        """
        try:
            if self.db_type == DatabaseType.SUPABASE.value:
                # Build the query
                table = self.client.table(collection)
                for key, value in query.items():
                    table = table.eq(key, value)
                result = table.update(update).execute()
                return len(result.data) > 0
                
            elif self.db_type == DatabaseType.MONGODB.value:
                result = self.db[collection].update_one(query, {"$set": update})
                return result.modified_count > 0
                
        except Exception as e:
            logger.error(f"Update operation failed: {str(e)}")
            raise
    
    def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        Delete a single document/record.
        
        Args:
            collection: Table/collection name
            query: Query filter to find document
            
        Returns:
            True if deletion successful
        """
        try:
            if self.db_type == DatabaseType.SUPABASE.value:
                table = self.client.table(collection)
                for key, value in query.items():
                    table = table.eq(key, value)
                result = table.delete().execute()
                return len(result.data) > 0
                
            elif self.db_type == DatabaseType.MONGODB.value:
                result = self.db[collection].delete_one(query)
                return result.deleted_count > 0
                
        except Exception as e:
            logger.error(f"Delete operation failed: {str(e)}")
            raise
    
    def close(self):
        """Close database connection"""
        try:
            if self.db_type == DatabaseType.MONGODB.value and self.client:
                self.client.close()
                logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}")


def get_db_connection(db_type: str = None, credentials: Dict[str, str] = None) -> DatabaseClient:
    """
    Factory function to get database connection.
    
    Args:
        db_type: Database type ('supabase' or 'mongodb')
        credentials: Connection credentials
        
    Returns:
        DatabaseClient instance
    """
    # Try to get from environment variables if not provided
    if not db_type:
        db_type = os.getenv('DB_TYPE', 'mongodb')
    
    if not credentials:
        credentials = {}
        if db_type.lower() == 'supabase':
            credentials = {
                'supabase_url': os.getenv('SUPABASE_URL'),
                'supabase_key': os.getenv('SUPABASE_KEY')
            }
        elif db_type.lower() == 'mongodb':
            credentials = {
                'mongodb_uri': os.getenv('MONGODB_URI'),
                'database_name': os.getenv('DB_NAME', 'multimodel_rag')
            }
    
    return DatabaseClient(db_type, credentials)


class DBClient:
    """Simple persistence layer storing queries in the local SQLite history DB."""

    def __init__(self, db_path: Optional[str] = None):
        resolved_path = db_path or os.getenv("SQLITE_DB_PATH", "chat_history.db")
        self.dao = ChatHistoryDAO(db_path=resolved_path)

    def save_query(
        self,
        question: str,
        final_answer: str,
        multi_llm_answers: List[Dict[str, any]],
        session_id: Optional[str] = None,
    ) -> None:
        session = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.dao.save_message(session, "user", question, metadata={"multi_llm": multi_llm_answers})
        self.dao.save_message(session, "assistant", final_answer, metadata={"multi_llm": multi_llm_answers})


# Example usage and testing
if __name__ == "__main__":
    # This section is for testing purposes only
    print("Database Client Module Loaded")
    print("Use get_db_connection() to initialize a database connection")