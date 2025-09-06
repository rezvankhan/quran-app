import sqlite3
import os

def create_tables():
    try:
        # استفاده از path مطلق
        db_path = os.path.join(os.path.dirname(__file__), 'quran_db.sqlite3')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ایجاد جدول users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                full_name TEXT,
                email TEXT,
                grade TEXT,
                specialty TEXT,
                approved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # اضافه کردن این بخش برای جدول students
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                level TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        print("✅ جداول در SQLite ایجاد شدند")
    except Exception as err:
        print(f"❌ خطا در ایجاد جداول: {err}")

if __name__ == "__main__":
    create_tables()