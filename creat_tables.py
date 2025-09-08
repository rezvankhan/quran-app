# creat_tables.py - پایگاه داده کامل
import sqlite3
import os

def create_tables():
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'quran_db.sqlite3')
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
        
        # جدول lessons - دروس
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                order_index INTEGER,
                duration INTEGER,
                video_url TEXT,
                resources TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE
            )
        """)
        
        # جدول progress - پیشرفت دانشجویان
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                completion_date TIMESTAMP,
                score DECIMAL(5,2),
                feedback TEXT,
                FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE,
                UNIQUE(student_id, lesson_id)
            )
        """)
        
        # جدول payments - پرداخت‌ها
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                class_id INTEGER,
                amount DECIMAL(10,2) NOT NULL,
                currency TEXT DEFAULT 'USDT',
                payment_method TEXT,
                transaction_id TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE
            )
        """)
        
        # جدول messages - پیام‌ها
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                class_id INTEGER,
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ پایگاه داده کامل با تمام جداول ایجاد شد")
        
    except Exception as err:
        print(f"❌ خطا در ایجاد پایگاه داده: {err}")

def init_sample_data():
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'quran_db.sqlite3')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # داده‌های نمونه برای تست
        cursor.execute("""
            INSERT OR IGNORE INTO users 
            (username, password, role, full_name, email, approved) 
            VALUES 
            ('admin', 'admin123', 'admin', 'مدیر سیستم', 'admin@quran.com', 1),
            ('teacher1', 'teacher123', 'teacher', 'استاد احمد', 'teacher1@quran.com', 1),
            ('student1', 'student123', 'student', 'دانشجو محمد', 'student1@quran.com', 1)
        """)
        
        conn.commit()
        conn.close()
        print("✅ داده‌های نمونه اضافه شدند")
        
    except Exception as err:
        print(f"❌ خطا در افزودن داده‌های نمونه: {err}")

if __name__ == "__main__":
    create_tables()
    init_sample_data()
