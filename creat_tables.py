# creat_tables.py - پایگاه داده کامل
import sqlite3
import os

def create_tables():
    try:
        # استفاده از مسیر یکسان با backend
        if 'RENDER' in os.environ:
            db_path = '/tmp/quran_db.sqlite3'
        else:
            db_path = 'quran_db.sqlite3'
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # جدول users - اصلی
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                grade TEXT,
                specialty TEXT,
                approved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول students - اطلاعات اضافی دانشجویان
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                level TEXT DEFAULT 'Beginner',
                progress INTEGER DEFAULT 0,
                total_classes INTEGER DEFAULT 0,
                completed_classes INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id)
            )
        """)
        
        # جدول teachers - اطلاعات اضافی معلمان
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                experience TEXT,
                bio TEXT,
                hourly_rate DECIMAL(10,2) DEFAULT 0,
                rating DECIMAL(3,2) DEFAULT 0,
                total_students INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id)
            )
        """)
        
        # جدول classes - کلاس‌ها
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
                start_date DATE,
                end_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # جدول enrollments - ثبت‌نام‌ها
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                progress INTEGER DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE,
                UNIQUE(student_id, class_id)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ پایگاه داده کامل با تمام جداول ایجاد شد")
        
    except Exception as err:
        print(f"❌ خطا در ایجاد پایگاه داده: {err}")

def init_sample_data():
    try:
        if 'RENDER' in os.environ:
            db_path = '/tmp/quran_db.sqlite3'
        else:
            db_path = 'quran_db.sqlite3'
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # داده‌های نمونه برای تست
        import hashlib
        def hash_pw(password):
            return hashlib.sha256(password.encode()).hexdigest()
        
        # حذف داده‌های قدیمی اگر وجود دارند
        cursor.execute("DELETE FROM users")
        
        # درج داده‌های نمونه
        cursor.execute("""
            INSERT INTO users 
            (username, password, role, full_name, email, approved) 
            VALUES 
            (?, ?, ?, ?, ?, ?)
        """, ('admin', hash_pw('admin123'), 'admin', 'مدیر سیستم', 'admin@quran.com', 1))
        
        cursor.execute("""
            INSERT INTO users 
            (username, password, role, full_name, email, approved) 
            VALUES 
            (?, ?, ?, ?, ?, ?)
        """, ('teacher1', hash_pw('teacher123'), 'teacher', 'استاد احمد', 'teacher1@quran.com', 1))
        
        cursor.execute("""
            INSERT INTO users 
            (username, password, role, full_name, email, approved) 
            VALUES 
            (?, ?, ?, ?, ?, ?)
        """, ('student1@quran.com', hash_pw('student123'), 'student', 'دانشجو محمد', 'student1@quran.com', 1))
        
        # اضافه کردن به جداول فرعی
        cursor.execute("INSERT INTO teachers (user_id) VALUES (2)")
        cursor.execute("INSERT INTO students (user_id, level) VALUES (3, 'Beginner')")
        
        conn.commit()
        conn.close()
        print("✅ داده‌های نمونه اضافه شدند")
        
    except Exception as err:
        print(f"❌ خطا در افزودن داده‌های نمونه: {err}")

if __name__ == "__main__":
    create_tables()
    init_sample_data()
