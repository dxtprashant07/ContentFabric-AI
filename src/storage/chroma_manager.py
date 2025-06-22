import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import hashlib

class SimpleStorageManager:
    """Simple file-based storage manager using JSON and SQLite."""
    
    def __init__(self, db_path: str = "./data/content.db", data_dir: str = "./data/content"):
        self.db_path = Path(db_path)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp TEXT NOT NULL,
                version INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT NOT NULL,
                output_type TEXT NOT NULL,
                output_content TEXT NOT NULL,
                metadata TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (content_hash) REFERENCES content_versions (content_hash)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_content(self, url: str, content: str, title: str = "", metadata: Optional[Dict] = None) -> str:
        """Store content and return content hash."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if content already exists
        cursor.execute('SELECT version FROM content_versions WHERE content_hash = ?', (content_hash,))
        existing = cursor.fetchone()
        
        if existing:
            version = existing[0] + 1
        else:
            version = 1
        
        # Store content
        cursor.execute('''
            INSERT OR REPLACE INTO content_versions 
            (content_hash, url, title, content, metadata, timestamp, version)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            content_hash,
            url,
            title,
            content,
            json.dumps(metadata) if metadata else None,
            datetime.now().isoformat(),
            version
        ))
        
        conn.commit()
        conn.close()
        
        return content_hash
    
    def store_ai_output(self, content_hash: str, output_type: str, output_content: str, metadata: Optional[Dict] = None):
        """Store AI-generated output."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_outputs (content_hash, output_type, output_content, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            content_hash,
            output_type,
            output_content,
            json.dumps(metadata) if metadata else None,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_content(self, content_hash: str) -> Optional[Dict]:
        """Retrieve content by hash."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, title, content, metadata, timestamp, version
            FROM content_versions WHERE content_hash = ?
        ''', (content_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'url': row[0],
                'title': row[1],
                'content': row[2],
                'metadata': json.loads(row[3]) if row[3] else None,
                'timestamp': row[4],
                'version': row[5],
                'content_hash': content_hash
            }
        return None
    
    def get_ai_outputs(self, content_hash: str) -> List[Dict]:
        """Retrieve all AI outputs for a content hash."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT output_type, output_content, metadata, timestamp
            FROM ai_outputs WHERE content_hash = ?
            ORDER BY timestamp DESC
        ''', (content_hash,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'output_type': row[0],
                'output_content': row[1],
                'metadata': json.loads(row[2]) if row[2] else None,
                'timestamp': row[3]
            }
            for row in rows
        ]
    
    def search_content(self, query: str, limit: int = 10) -> List[Dict]:
        """Simple text search in content."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content_hash, url, title, content, timestamp
            FROM content_versions 
            WHERE content LIKE ? OR title LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'content_hash': row[0],
                'url': row[1],
                'title': row[2],
                'content': row[3][:200] + '...' if len(row[3]) > 200 else row[3],
                'timestamp': row[4]
            }
            for row in rows
        ]
    
    def get_all_content(self, limit: int = 50) -> List[Dict]:
        """Get all stored content."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content_hash, url, title, timestamp, version
            FROM content_versions 
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'content_hash': row[0],
                'url': row[1],
                'title': row[2],
                'timestamp': row[3],
                'version': row[4]
            }
            for row in rows
        ]

# Global instance
_storage_manager = None

def get_storage_manager() -> SimpleStorageManager:
    """Get the global storage manager instance."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = SimpleStorageManager()
    return _storage_manager


class ChromaDBManager:
    """ChromaDB manager for the API."""
    
    def __init__(self, db_path: str = "./data/chroma_db"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.storage_manager = SimpleStorageManager()
    
    def store_content_version(self, content: Dict, version_info: Dict) -> str:
        """Store content version and return version ID."""
        content_hash = self.storage_manager.store_content(
            url=version_info.get('url', ''),
            content=content.get('content', ''),
            title=content.get('title', ''),
            metadata=version_info
        )
        return content_hash
    
    def get_content_version(self, version_id: str) -> Optional[Dict]:
        """Get content version by ID."""
        return self.storage_manager.get_content(version_id)
    
    def get_all_versions(self, url: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get all content versions."""
        return self.storage_manager.get_all_content(limit=limit)
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        all_content = self.storage_manager.get_all_content(limit=1000)
        return {
            "total_entries": len(all_content),
            "storage_path": str(self.db_path)
        }
    
    def delete_version(self, version_id: str) -> bool:
        """Delete a version (not implemented in SimpleStorageManager)."""
        # SimpleStorageManager doesn't support deletion
        return False


def get_chroma_manager() -> ChromaDBManager:
    """Get ChromaDB manager instance."""
    return ChromaDBManager() 