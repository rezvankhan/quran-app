# creat_tables.py - کامل
import sqlite3
import os
import hashlib

def create_tables():
    try:
        if 'RENDER' in os.environ:
            db_path = '/tmp/quran_db.sqlite3'
        else:
            db_path = 'quran_db.sqlite3'
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                full_name TEXT,
                email TEXT UNIQUE,
                specialty TEXT,
                approved BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                level TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                experience TEXT,
                bio TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                level TEXT DEFAULT 'Beginner',
                category TEXT,
                duration INTEGER DEFAULT 60,
                price DECIMAL(10,2) DEFAULT 0,
                max_students INTEGER DEFAULT 10,
                schedule TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                progress INTEGER DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES users (id),
                FOREIGN KEY (class_id) REFERENCES classes (id),
                UNIQUE(student_id, class_id)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database tables created successfully")
        
    except Exception as err:
        print(f"❌ Error creating tables: {err}")

def init_sample_data():
    try:
        if 'RENDER' in os.environ:
            db_path = '/tmp/quran_db.sqlite3'
        else:
            db_path = 'quran_db.sqlite3'
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # پاک کردن داده‌های قبلی
        cursor.execute("DELETE FROM enrollments")
        cursor.execute("DELETE FROM classes")
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM teachers")
        cursor.execute("DELETE FROM users")
        
        # اضافه کردن داده‌های نمونه
        def hash_pw(password):
            return hashlib.sha256(password.encode()).hexdigest()
        
        # کاربران نمونه
        users = [
            ('admin', hash_pw('admin123'), 'admin', 'مدیر سیستم', 'admin@quran.com', '', True),
            ('teacher1', hash_pw('teacher123'), 'teacher', 'استاد احمد', 'teacher1@quran.com', 'Quran Recitation', True),
            ('student1', hash_pw('student123'), 'student', 'دانشجو محمد', 'student1@quran.com', '', True),
            ('student2', hash_pw('student123'), 'student', 'دانشجو فاطمه', 'student2@quran.com', '', True)
        ]
        
        for user in users:
            cursor.execute(
                "INSERT INTO users (username, password, role, full_name, email, specialty, approved) VALUES (?, ?, ?, ?, ?, ?, ?)",
                user
            )
        
        # دانشجویان
        cursor.execute("INSERT INTO students (user_id, level) VALUES (3, 'Intermediate')")
        cursor.execute("INSERT INTO students (user_id, level) VALUES (4, 'Beginner')")
        
        # معلمان
        cursor.execute("INSERT INTO teachers (user_id, experience) VALUES (2, '5 years')")
        
        # کلاس‌های نمونه
        classes = [
            (2, 'Basic Quran Reading', 'Learn to read Quran from basics', 'Beginner', 'Recitation', 60, 0, 20, 'Mon, Wed, Fri 10:00-11:00'),
            (2, 'Tajweed Fundamentals', 'Learn proper pronunciation rules', 'Intermediate', 'Tajweed', 60, 0, 15, 'Tue, Thu 14:00-15:00'),
            (2, 'Advanced Recitation', 'Master Quran recitation', 'Advanced', 'Recitation', 90, 0, 10, 'Sat, Sun 09:00-10:30')
        ]
        
        for class_data in classes:
            cursor.execute(
                "INSERT INTO classes (teacher_id, title, description, level, category, duration, price, max_students, schedule) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                class_data
            )
        
        # ثبت‌نام‌های نمونه
        enrollments = [
            (3, 1, 25),
            (3, 2, 50),
            (4, 1, 15)
        ]
        
        for enrollment in enrollments:
            cursor.execute(
                "INSERT INTO enrollments (student_id, class_id, progress) VALUES (?, ?, ?)",
                enrollment
            )
        
        conn.commit()
        conn.close()
        print("✅ Sample data inserted successfully")
        
    except Exception as err:
        print(f"❌ Error inserting sample data: {err}")

if __name__ == "__main__":
    create_tables()
    init_sample_data()
