import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# استفاده از DATABASE_URL از environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

@contextmanager
def get_db_connection(database=None):
    conn = None
    cursor = None
    
    try:
        # استفاده از DATABASE_URL اگر موجود باشد
        if DATABASE_URL:
            parsed_url = urlparse(DATABASE_URL)
            conn = psycopg2.connect(
                host=parsed_url.hostname,
                database=parsed_url.path[1:],  # حذف slash اول
                user=parsed_url.username,
                password=parsed_url.password,
                port=parsed_url.port
            )
        else:
            # برای توسعه محلی (Fallback)
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=database,
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", ""),
                port=os.getenv("DB_PORT", "5432")
            )
        
        cursor = conn.cursor()
        yield cursor, conn
        conn.commit()
        
    except Exception as err:
        print(f"❌ خطای دیتابیس: {err}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_tables():
    try:
        with get_db_connection() as (cursor, conn):
            # ایجاد جدول users (برای PostgreSQL)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'student',
                    approved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # ایجاد جدول lessons (برای PostgreSQL)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    teacher_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            
            print("✅ جداول در PostgreSQL ایجاد شدند")
            
    except Exception as err:
        print(f"❌ خطا در ایجاد جداول: {err}")

if __name__ == "__main__":
    create_tables()