# creat_tables.py - کامل
import sqlite3
import os
from passlib.context import CryptContext

# استفاده از همان سیستم هش کردن backend.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

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
        
        # بررسی اگر داده‌ها قبلاً وجود دارند
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("⚠️  Data already exists, skipping sample data insertion")
            conn.close()
            return
        
        # اضافه کردن داده‌های نمونه
        users = [
            ('admin@quran.com', get_password_hash('admin123'), 'admin', 'مدیر سیستم', 'admin@quran.com', '', True),
            ('teacher1', get_password_hash('teacher123'), 'teacher', 'استاد احمد', 'teacher1@quran.com', 'Quran Recitation', True),
            ('student1@quran.com', get_password_hash('student123'), 'student', 'دانشجو محمد', 'student1@quran.com', '', True),
            ('student2@quran.com', get_password_hash('student123'), 'student', 'دانشجو فاطمه', 'student2@quran.com', '', True)
        ]
        
        user_ids = []
        for user in users:
            cursor.execute(
                "INSERT INTO users (username, password, role, full_name, email, specialty, approved) VALUES (?, ?, ?, ?, ?, ?, ?)",
                user
            )
            user_ids.append(cursor.lastrowid)
        
        # دانشجویان
        cursor.execute("INSERT INTO students (user_id, level) VALUES (?, ?)", (user_ids[2], 'Intermediate'))
        cursor.execute("INSERT INTO students (user_id, level) VALUES (?, ?)", (user_ids[3], 'Beginner'))
        
        # معلمان
        cursor.execute("INSERT INTO teachers (user_id, experience) VALUES (?, ?)", (user_ids[1], '5 years experience'))
        
        # کلاس‌های نمونه
        classes = [
            (user_ids[1], 'Basic Quran Reading', 'Learn to read Quran from basics', 'Beginner', 'Recitation', 60, 0, 20, 'Mon, Wed, Fri 10:00-11:00'),
            (user_ids[1], 'Tajweed Fundamentals', 'Learn proper pronunciation rules', 'Intermediate', 'Tajweed', 60, 0, 15, 'Tue, Thu 14:00-15:00'),
            (user_ids[1], 'Advanced Recitation', 'Master Quran recitation', 'Advanced', 'Recitation', 90, 0, 10, 'Sat, Sun 09:00-10:30')
        ]
        
        class_ids = []
        for class_data in classes:
            cursor.execute(
                "INSERT INTO classes (teacher_id, title, description, level, category, duration, price, max_students, schedule) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                class_data
            )
            class_ids.append(cursor.lastrowid)
        
        # ثبت‌نام‌های نمونه
        enrollments = [
            (user_ids[2], class_ids[0], 25),
            (user_ids[2], class_ids[1], 50),
            (user_ids[3], class_ids[0], 15)
        ]
        
        for enrollment in enrollments:
            try:
                cursor.execute(
                    "INSERT INTO enrollments (student_id, class_id, progress) VALUES (?, ?, ?)",
                    enrollment
                )
            except sqlite3.IntegrityError:
                print(f"⚠️  Duplicate enrollment skipped: {enrollment}")
                continue
        
        conn.commit()
        conn.close()
        print("✅ Sample data inserted successfully")
        print("\n📋 Sample Login Credentials:")
        print("Admin: admin@quran.com / admin123")
        print("Teacher: teacher1 / teacher123")
        print("Student 1: student1@quran.com / student123")
        print("Student 2: student2@quran.com / student123")
        
    except Exception as err:
        print(f"❌ Error inserting sample data: {err}")

def check_existing_data():
    """بررسی وجود داده در دیتابیس"""
    try:
        if 'RENDER' in os.environ:
            db_path = '/tmp/quran_db.sqlite3'
        else:
            db_path = 'quran_db.sqlite3'
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM classes")
        class_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM enrollments")
        enrollment_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 Current database status:")
        print(f"   Users: {user_count}")
        print(f"   Classes: {class_count}")
        print(f"   Enrollments: {enrollment_count}")
        
        return user_count > 0
        
    except Exception as err:
        print(f"❌ Error checking database: {err}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database setup...")
    
    # بررسی وجود داده‌ها
    has_data = check_existing_data()
    
    if has_data:
        print("\n⚠️  Database already has data. Do you want to:")
        print("1. Recreate tables and insert sample data (ALL DATA WILL BE LOST!)")
        print("2. Skip data insertion")
        
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            # پاک کردن و ایجاد مجدد
            create_tables()
            init_sample_data()
        else:
            print("✅ Skipping data insertion")
    else:
        # ایجاد جداول و داده‌های نمونه
        create_tables()
        init_sample_data()
    
    print("✅ Database setup completed!")
