import sqlite3
from contextlib import contextmanager
import os

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('quran_db.sqlite3')
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        yield cursor, conn
        conn.commit()
    except sqlite3.Error as err:
        print(f"❌ خطای دیتابیس: {err}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def create_tables():
    try:
        with get_db_connection() as (cursor, conn):
            # ایجاد جدول users
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'student',
                    approved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            print("✅ جداول در SQLite ایجاد شدند")
    except Exception as err:
        print(f"❌ خطا در ایجاد جداول: {err}")

if __name__ == "__main__":
    create_tables()
    create_tables()

