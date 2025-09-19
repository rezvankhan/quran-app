# creat_tables.py - کامل با جداول دروس و پیشرفت
import sqlite3
import os
from passlib.context import CryptContext

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
        
        # جداول اصلی موجود
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                full_name TEXT,
                email TEXT UNIQUE,
                specialty TEXT,
                wallet_balance DECIMAL(10,2) DEFAULT 0,
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
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                questions TEXT,
                duration INTEGER DEFAULT 60,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes (id),
                FOREIGN KEY (teacher_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exam_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                score INTEGER,
                answers TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exam_id) REFERENCES exams (id),
                FOREIGN KEY (student_id) REFERENCES users (id),
                UNIQUE(exam_id, student_id)
            )
        """)
        
        # جداول جدید برای فاز یک - سیستم آموزشی
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content_type TEXT DEFAULT 'text',
                content_url TEXT,
                duration INTEGER DEFAULT 0,
                order_index INTEGER DEFAULT 0,
                description TEXT,
                is_published BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                is_completed BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP,
                progress_percentage INTEGER DEFAULT 0,
                last_position INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE,
                UNIQUE(student_id, lesson_id)
            )
        """)
        
        # ایجاد ایندکس برای بهبود عملکرد
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lessons_class_id ON lessons(class_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lessons_order ON lessons(class_id, order_index)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lesson_progress_student ON lesson_progress(student_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lesson_progress_lesson ON lesson_progress(lesson_id)")
        
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
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("⚠️  Data already exists, skipping sample data insertion")
            conn.close()
            return
        
        users = [
            ('admin@quran.com', get_password_hash('admin123'), 'admin', 'Admin User', 'admin@quran.com', '', 100, True),
            ('teacher1', get_password_hash('teacher123'), 'teacher', 'استاد احمد', 'teacher1@quran.com', 'Quran Recitation', 500, True),
            ('student1@quran.com', get_password_hash('student123'), 'student', 'دانشجو محمد', 'student1@quran.com', '', 50, True),
            ('student2@quran.com', get_password_hash('student123'), 'student', 'دانشجو فاطمه', 'student2@quran.com', '', 75, True)
        ]
        
        user_ids = []
        for user in users:
            cursor.execute(
                "INSERT INTO users (username, password, role, full_name, email, specialty, wallet_balance, approved) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                user
            )
            user_ids.append(cursor.lastrowid)
        
        cursor.execute("INSERT INTO students (user_id, level) VALUES (?, ?)", (user_ids[2], 'Intermediate'))
        cursor.execute("INSERT INTO students (user_id, level) VALUES (?, ?)", (user_ids[3], 'Beginner'))
        
        cursor.execute("INSERT INTO teachers (user_id, experience) VALUES (?, ?)", (user_ids[1], '5 years experience'))
        
        classes = [
            (user_ids[1], 'Basic Quran Reading', 'Learn to read Quran from basics', 'Beginner', 'Recitation', 60, 0, 20, 'Mon, Wed, Fri 10:00-11:00'),
            (user_ids[1], 'Tajweed Fundamentals', 'Learn proper pronunciation rules', 'Intermediate', 'Tajweed', 60, 25, 15, 'Tue, Thu 14:00-15:00'),
            (user_ids[1], 'Advanced Recitation', 'Master Quran recitation', 'Advanced', 'Recitation', 90, 50, 10, 'Sat, Sun 09:00-10:30')
        ]
        
        class_ids = []
        for class_data in classes:
            cursor.execute(
                "INSERT INTO classes (teacher_id, title, description, level, category, duration, price, max_students, schedule) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                class_data
            )
            class_ids.append(cursor.lastrowid)
        
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
        
        # اضافه کردن داده‌های نمونه برای دروس
        lessons = [
            (class_ids[0], 'Introduction to Arabic Letters', 'text', None, 15, 1, 'Learn the basics of Arabic alphabet', True),
            (class_ids[0], 'Basic Pronunciation', 'video', 'https://example.com/video1.mp4', 20, 2, 'Practice basic sounds', True),
            (class_ids[0], 'Reading Practice', 'text', None, 25, 3, 'Practice reading simple words', True),
            (class_ids[1], 'Tajweed Rules Overview', 'text', None, 30, 1, 'Introduction to Tajweed rules', True),
            (class_ids[1], 'Practice Session 1', 'audio', 'https://example.com/audio1.mp3', 25, 2, 'First practice session', True),
            (class_ids[2], 'Advanced Techniques', 'video', 'https://example.com/video2.mp4', 40, 1, 'Learn advanced recitation techniques', True)
        ]
        
        for lesson in lessons:
            cursor.execute(
                "INSERT INTO lessons (class_id, title, content_type, content_url, duration, order_index, description, is_published) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                lesson
            )
        
        conn.commit()
        conn.close()
        print("✅ Sample data inserted successfully")
        print("\n📋 Sample Login Credentials:")
        print("Admin: admin@quran.com / admin123 (Balance: $100)")
        print("Teacher: teacher1 / teacher123 (Balance: $500)")
        print("Student 1: student1@quran.com / student123 (Balance: $50)")
        print("Student 2: student2@quran.com / student123 (Balance: $75)")
        print("\n📚 Sample courses now include lessons for testing")
        
    except Exception as err:
        print(f"❌ Error inserting sample data: {err}")

if __name__ == "__main__":
    print("🚀 Starting database setup...")
    create_tables()
    init_sample_data()
    print("✅ Database setup completed!")
