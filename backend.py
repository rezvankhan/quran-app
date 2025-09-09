# backend.py - کامل با endpoint جدید
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3
import hashlib
import os
from datetime import datetime
from contextlib import asynccontextmanager
import logging

# تنظیمات logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تشخیص محیط
def get_db_connection():
    if 'RENDER' in os.environ:
        db_path = '/tmp/quran_db.sqlite3'
    else:
        db_path = 'quran_db.sqlite3'
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# تابع کمکی برای تبدیل Row به Dictionary
def row_to_dict(row):
    """تبدیل sqlite3.Row به dictionary"""
    if row is None:
        return None
    return dict(row)

def rows_to_dict_list(rows):
    """تبدیل لیست sqlite3.Row به لیست dictionary"""
    return [dict(row) for row in rows] if rows else []

# مدل‌های داده
class StudentRegister(BaseModel):
    name: str
    email: str
    password: str
    level: str

class TeacherRegister(BaseModel):
    username: str
    password: str
    full_name: str
    email: str
    specialty: str

class LoginRequest(BaseModel):
    username: str
    password: str

class EnrollmentRequest(BaseModel):
    student_id: int

class CourseCreate(BaseModel):
    title: str
    description: str
    level: str = "Beginner"
    category: str
    duration: int = 60
    price: float = 0
    max_students: int = 10
    schedule: str

# تابع hash کردن password
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ایجاد جداول و داده‌های تست
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # ایجاد جداول
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
        
        # اضافه کردن داده‌های تست اگر وجود ندارند
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        user_count = row_to_dict(result)['count'] if result else 0
        
        if user_count == 0:
            logger.info("Adding test data to database...")
            
            # کاربران تست
            test_users = [
                ('admin@quran.com', hash_password('admin123'), 'admin', 'Admin User', 'admin@quran.com', '', True),
                ('teacher1', hash_password('teacher123'), 'teacher', 'استاد احمد', 'teacher1@quran.com', 'Quran Recitation', True),
                ('student1@quran.com', hash_password('student123'), 'student', 'دانشجو محمد', 'student1@quran.com', '', True),
                ('student2@quran.com', hash_password('student123'), 'student', 'دانشجو فاطمه', 'student2@quran.com', '', True)
            ]
            
            for user in test_users:
                try:
                    cursor.execute(
                        "INSERT INTO users (username, password, role, full_name, email, specialty, approved) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        user
                    )
                    user_id = cursor.lastrowid
                    
                    if user[2] == 'student':
                        cursor.execute(
                            "INSERT INTO students (user_id, level) VALUES (?, ?)",
                            (user_id, 'Beginner')
                        )
                    elif user[2] == 'teacher':
                        cursor.execute(
                            "INSERT INTO teachers (user_id, experience) VALUES (?, ?)",
                            (user_id, '5 years experience')
                        )
                        
                except sqlite3.IntegrityError as e:
                    logger.warning(f"User already exists: {user[0]}")
                    continue
            
            # کلاس‌های تست
            cursor.execute("SELECT id FROM users WHERE username = 'teacher1'")
            teacher_result = cursor.fetchone()
            if teacher_result:
                teacher_id = row_to_dict(teacher_result)['id']
                
                test_classes = [
                    (teacher_id, 'Basic Quran Reading', 'Learn to read Quran from basics', 'Beginner', 'Recitation', 60, 0, 20, 'Mon, Wed, Fri 10:00-11:00'),
                    (teacher_id, 'Tajweed Fundamentals', 'Learn proper pronunciation rules', 'Intermediate', 'Tajweed', 60, 0, 15, 'Tue, Thu 14:00-15:00'),
                    (teacher_id, 'Advanced Recitation', 'Master Quran recitation', 'Advanced', 'Recitation', 90, 0, 10, 'Sat, Sun 09:00-10:30')
                ]
                
                for class_data in test_classes:
                    cursor.execute(
                        "INSERT INTO classes (teacher_id, title, description, level, category, duration, price, max_students, schedule) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        class_data
                    )
                
                # ثبت‌نام‌های تست
                cursor.execute("SELECT id FROM users WHERE email = 'student1@quran.com'")
                student1_result = cursor.fetchone()
                cursor.execute("SELECT id FROM users WHERE email = 'student2@quran.com'")
                student2_result = cursor.fetchone()
                
                if student1_result and student2_result:
                    student1_id = row_to_dict(student1_result)['id']
                    student2_id = row_to_dict(student2_result)['id']
                    
                    test_enrollments = [
                        (student1_id, 1, 25),
                        (student1_id, 2, 50),
                        (student2_id, 1, 15)
                    ]
                    
                    for enrollment in test_enrollments:
                        try:
                            cursor.execute(
                                "INSERT INTO enrollments (student_id, class_id, progress) VALUES (?, ?, ?)",
                                enrollment
                            )
                        except sqlite3.IntegrityError:
                            continue
            
            conn.commit()
            logger.info("Test data added successfully")
        
        conn.close()
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Quran App API", "status": "running", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as user_count FROM users")
        result = cursor.fetchone()
        user_count = row_to_dict(result)['user_count'] if result else 0
        conn.close()
        
        return {
            "status": "healthy", 
            "timestamp": datetime.now().isoformat(),
            "user_count": user_count,
            "environment": "Render" if 'RENDER' in os.environ else "Local"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/debug/users")
async def debug_users():
    """Endpoint برای دیباگ کاربران"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, full_name FROM users")
        users = cursor.fetchall()
        conn.close()
        
        return {"users": rows_to_dict_list(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/passwords")
async def debug_passwords():
    """Endpoint برای دیباگ پسوردها"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password, role FROM users")
        users = cursor.fetchall()
        conn.close()
        
        return {"users": rows_to_dict_list(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/reset-passwords")
async def reset_passwords():
    """ریست کردن پسورد همه کاربران به مقدار پیش‌فرض"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # پسوردهای پیش‌فرض
        default_passwords = {
            "admin@quran.com": "admin123",
            "teacher1": "teacher123", 
            "student1@quran.com": "student123",
            "student2@quran.com": "student123",
            "testuser@example.com": "simplepassword"
        }
        
        updated_count = 0
        for username, password in default_passwords.items():
            hashed_password = hash_password(password)
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (hashed_password, username)
            )
            if cursor.rowcount > 0:
                updated_count += 1
                logger.info(f"Reset password for {username}")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True, 
            "message": f"Passwords reset successfully for {updated_count} users",
            "updated_count": updated_count
        }
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register/student")
async def register_student(student: StudentRegister):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(student.password)
        logger.info(f"Registering student: {student.email}")
        
        cursor.execute(
            "INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
            (student.email, hashed_password, student.name, student.email, 'student')
        )
        
        user_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO students (user_id, level) VALUES (?, ?)",
            (user_id, student.level)
        )
        
        conn.commit()
        conn.close()
        
        return {"message": "Student registered successfully", "user_id": user_id, "success": True}
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        logger.error(f"Student registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register/teacher")
async def register_teacher(teacher: TeacherRegister):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(teacher.password)
        logger.info(f"Registering teacher: {teacher.username}")
        
        cursor.execute(
            "INSERT INTO users (username, password, full_name, email, specialty, role) VALUES (?, ?, ?, ?, ?, ?)",
            (teacher.username, hashed_password, teacher.full_name, teacher.email, teacher.specialty, 'teacher')
        )
        
        user_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO teachers (user_id) VALUES (?)",
            (user_id,)
        )
        
        conn.commit()
        conn.close()
        
        return {"message": "Teacher registered successfully", "user_id": user_id, "success": True}
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as e:
        logger.error(f"Teacher registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(login_data: LoginRequest):
    try:
        logger.info(f"Login attempt: username={login_data.username}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(login_data.password)
        logger.info(f"Password hash: {hashed_password}")
        
        # دیباگ: نمایش تمام کاربران
        cursor.execute("SELECT username, email, password FROM users")
        all_users = cursor.fetchall()
        logger.info(f"Users in database: {rows_to_dict_list(all_users)}")
        
        cursor.execute(
            "SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?",
            (login_data.username, login_data.username, hashed_password)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            user_dict = row_to_dict(user)
            logger.info(f"Login successful for user: {user_dict['username']}")
            return {
                "success": True,
                "user": {
                    "id": user_dict['id'],
                    "username": user_dict['username'],
                    "full_name": user_dict['full_name'],
                    "email": user_dict['email'],
                    "role": user_dict['role'],
                    "specialty": user_dict.get('specialty', ''),
                    "approved": bool(user_dict['approved'])
                }
            }
        else:
            logger.warning("Login failed: Invalid credentials")
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/courses")
async def get_courses():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, u.full_name as teacher_name 
            FROM classes c 
            JOIN users u ON c.teacher_id = u.id 
            WHERE c.status = 'active'
        """)
        
        courses = cursor.fetchall()
        conn.close()
        
        return {"courses": rows_to_dict_list(courses)}
        
    except Exception as e:
        logger.error(f"Get courses error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/my-courses/{user_id}")
async def get_my_courses(user_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, u.full_name as teacher_name, e.progress, e.enrolled_at
            FROM classes c
            JOIN enrollments e ON c.id = e.class_id
            JOIN users u ON c.teacher_id = u.id
            WHERE e.student_id = ? AND e.status = 'active'
        """, (user_id,))
        
        courses = cursor.fetchall()
        conn.close()
        
        return {"my_courses": rows_to_dict_list(courses)}
        
    except Exception as e:
        logger.error(f"Get my courses error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enroll/{class_id}")
async def enroll_student(class_id: int, request: EnrollmentRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM classes WHERE id = ? AND status = 'active'", (class_id,))
        class_data = cursor.fetchone()
        
        if not class_data:
            raise HTTPException(status_code=404, detail="Class not found")
        
        cursor.execute("SELECT * FROM users WHERE id = ? AND role = 'student'", (request.student_id,))
        student = cursor.fetchone()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        cursor.execute(
            "SELECT * FROM enrollments WHERE student_id = ? AND class_id = ?",
            (request.student_id, class_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already enrolled in this class")
        
        cursor.execute(
            "INSERT INTO enrollments (student_id, class_id, status) VALUES (?, ?, 'active')",
            (request.student_id, class_id)
        )
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Enrollment successful"}
        
    except Exception as e:
        logger.error(f"Enrollment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
async def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, full_name, email, role, approved FROM users")
        users = cursor.fetchall()
        
        conn.close()
        
        return {"users": rows_to_dict_list(users)}
        
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# endpoint جدید برای ایجاد دوره توسط معلم
@app.post("/teacher/courses")
async def create_course(course_data: CourseCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # برای تست از teacher_id=2 استفاده می‌کنیم (teacher1)
        # در واقعیت باید از authentication استفاده شود
        teacher_id = 2
        
        cursor.execute(
            """
            INSERT INTO classes (teacher_id, title, description, level, category, duration, price, max_students, schedule)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                teacher_id,
                course_data.title,
                course_data.description,
                course_data.level,
                course_data.category,
                course_data.duration,
                course_data.price,
                course_data.max_students,
                course_data.schedule
            )
        )
        
        conn.commit()
        course_id = cursor.lastrowid
        conn.close()
        
        return {
            "success": True, 
            "course_id": course_id, 
            "message": "Course created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating course: {str(e)}")

# endpoint جدید برای دریافت دوره‌های معلم
@app.get("/teacher/{teacher_id}/courses")
async def get_teacher_courses(teacher_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, COUNT(e.id) as enrolled_students
            FROM classes c
            LEFT JOIN enrollments e ON c.id = e.class_id
            WHERE c.teacher_id = ?
            GROUP BY c.id
        """, (teacher_id,))
        
        courses = cursor.fetchall()
        conn.close()
        
        return {"courses": rows_to_dict_list(courses)}
        
    except Exception as e:
        logger.error(f"Get teacher courses error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
