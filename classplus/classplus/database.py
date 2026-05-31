"""
Database layer for ClassPlus Telegram Bot
Handles user authentication, downloads, and other persistent data
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict

class Database:
    def __init__(self, db_path: str = "classplus_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                token TEXT NOT NULL,
                user_id_classplus INTEGER,
                org_code TEXT,
                mobile TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Downloads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                item_type TEXT NOT NULL,
                status TEXT NOT NULL,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Courses cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                course_name TEXT,
                course_data TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, token: str, user_id_cp: int, org_code: str, mobile: str) -> bool:
        """Add or update user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, token, user_id_classplus, org_code, mobile, last_login)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, token, user_id_cp, org_code, mobile))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user and their data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM downloads WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM courses_cache WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def add_download(self, user_id: int, item_name: str, item_type: str, status: str) -> bool:
        """Log a download"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO downloads (user_id, item_name, item_type, status)
                VALUES (?, ?, ?, ?)
            ''', (user_id, item_name, item_type, status))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def get_download_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's download history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM downloads 
                WHERE user_id = ? 
                ORDER BY downloaded_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def cache_course(self, user_id: int, course_id: int, course_name: str, course_data: str) -> bool:
        """Cache course data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO courses_cache (user_id, course_id, course_name, course_data)
                VALUES (?, ?, ?, ?)
            ''', (user_id, course_id, course_name, course_data))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def get_cached_course(self, user_id: int, course_id: int) -> Optional[str]:
        """Get cached course data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT course_data FROM courses_cache 
                WHERE user_id = ? AND course_id = ?
                ORDER BY cached_at DESC LIMIT 1
            ''', (user_id, course_id))
            
            row = cursor.fetchone()
            if row:
                return row[0]
            return None
        finally:
            conn.close()
    
    def get_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total downloads
            cursor.execute(
                'SELECT COUNT(*) FROM downloads WHERE user_id = ?', 
                (user_id,)
            )
            total_downloads = cursor.fetchone()[0]
            
            # Completed
            cursor.execute(
                'SELECT COUNT(*) FROM downloads WHERE user_id = ? AND status = ?',
                (user_id, 'completed')
            )
            completed = cursor.fetchone()[0]
            
            # Failed
            cursor.execute(
                'SELECT COUNT(*) FROM downloads WHERE user_id = ? AND status = ?',
                (user_id, 'failed')
            )
            failed = cursor.fetchone()[0]
            
            return {
                'total_downloads': total_downloads,
                'completed': completed,
                'failed': failed
            }
        finally:
            conn.close()
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """Clean up data older than specified days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM courses_cache 
                WHERE datetime(cached_at) < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            deleted = cursor.rowcount
            conn.commit()
            return deleted
        finally:
            conn.close()
