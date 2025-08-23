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
            tables = [
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'teacher', 'student') NOT NULL DEFAULT 'student',
                    approved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS lessons (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    teacher_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES users(id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS student_lessons (
                    student_id INT,
                    lesson_id INT,
                    progress INT DEFAULT 0,
                    PRIMARY KEY (student_id, lesson_id),
                    FOREIGN KEY (student_id) REFERENCES users(id),
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
                )
                """
            ]
            for table in tables:
                cursor.execute(table)
            print("✅ جداول ایجاد شدند")
    except mysql.connector.Error as err:
        print(f"❌ خطا در ایجاد جداول: {err}")

# اضافه کردن بخش اجرای مستقیم از main.py
if __name__ == "__main__":
    create_database()
    create_tables()