"""
Database Service
----------------
Handles persistent indexing of file metadata using SQLite.
Supports complex queries for the NLP-based search engine.
"""
import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.services.logger import logger

class DbService:
    """Manages the SQLite database for file metadata indexing."""
    
    def __init__(self, db_path: str = "config/metadata.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes the database schema if it doesn't exist."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE,
                    filename TEXT,
                    extension TEXT,
                    size INTEGER,
                    category TEXT,
                    created_at DATETIME,
                    modified_at DATETIME
                )
            ''')
            # Create indexes for faster searching
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_filename ON files(filename)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_extension ON files(extension)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON files(category)')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def upsert_file(self, file_path: Path):
        """Adds or updates a file's metadata in the index."""
        try:
            stats = file_path.stat()
            from src.core.classifier import classifier
            category = classifier.classify(file_path)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO files (path, filename, extension, size, category, created_at, modified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(file_path),
                file_path.name,
                file_path.suffix.lower(),
                stats.st_size,
                category,
                datetime.fromtimestamp(stats.st_ctime).isoformat(),
                datetime.fromtimestamp(stats.st_mtime).isoformat()
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            # Silent fail for transient file access issues during monitoring
            pass

    def remove_file(self, file_path: Path):
        """Removes a file from the index."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM files WHERE path = ?', (str(file_path),))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to remove file from index: {e}")

    def query_files(self, filters: Dict[str, Any]) -> List[Dict]:
        """
        Executes a search query based on filtered criteria.
        Expects keys like: filename, extension, category, min_size, max_size, date_after.
        """
        query = "SELECT path, filename, category, size FROM files WHERE 1=1"
        params = []
        
        if "filename" in filters:
            query += " AND filename LIKE ?"
            params.append(f"%{filters['filename']}%")
        
        if "extension" in filters:
            query += " AND extension = ?"
            params.append(filters['extension'].lower())
            
        if "category" in filters:
            query += " AND category = ?"
            params.append(filters['category'])
            
        if "min_size" in filters:
            query += " AND size >= ?"
            params.append(filters['min_size'])
            
        if "max_size" in filters:
            query += " AND size <= ?"
            params.append(filters['max_size'])
            
        if "date_after" in filters:
            query += " AND created_at >= ?"
            params.append(filters['date_after'])

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Search query failed: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the indexed files."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM files")
            count = cursor.fetchone()[0]
            
            # Get breakdown by category
            cursor.execute("SELECT category, COUNT(*) FROM files GROUP BY category")
            categories = dict(cursor.fetchall())
            
            conn.close()
            return {
                "total_files": count,
                "categories": categories,
                "db_path": self.db_path
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

db_service = DbService()
