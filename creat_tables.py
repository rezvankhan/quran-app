import mysql.connector
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "charset": "utf8mb4",
    "collation": "utf8mb4_general_ci"
}

@contextmanager
def get_db_connection(database=None):
    config = DB_CONFIG.copy()
    if database:
        config["database"] = database
    
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        yield cursor, conn
        conn.commit()
    except mysql.connector.Error as err:
        print(f"❌ خطای دیتابیس: {err}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_database():
    try:
        with get_db_connection() as (cursor, conn):
            cursor.execute("CREATE DATABASE IF NOT EXISTS quran_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
            print("✅ دیتابیس ایجاد شد")
    except mysql.connector.Error as err:
        print(f"❌ خطا در ایجاد دیتابیس: {err}")

def create_tables():
    try:
        with get_db_connection("quran_db") as (cursor, conn):
            # ایجاد جدول users
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'teacher', 'student') DEFAULT 'student',
                    approved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_username (username)
                ) ENGINE=InnoDB
            """)
            
            # ایجاد جدول lessons
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    teacher_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL,
                    INDEX idx_teacher (teacher_id)
                ) ENGINE=InnoDB
            """)
            
            print("✅ جداول ایجاد شدند")
    except mysql.connector.Error as err:
        print(f"❌ خطا در ایجاد جداول: {err}")

if __name__ == "__main__":
    create_database()
    create_tables()