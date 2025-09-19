# backend.py - کامل با کیف پول، آزمون، پرداخت و سیستم آموزشی جدید
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
import json

# تنظیمات logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تنظیمات JWT
SECRET_KEY = "your-secret-key-please-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# تشخیص محیط
def get_db_connection():
    if 'RENDER' in os.environ:
        db_path = '/tmp/quran_db.sqlite3'
    else:
        db_path = 'quran_db.sqlite3'
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

def rows_to_dict_list(rows):
    return [dict(row) for row in rows] if rows else []

# توابع Authentication
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        username: str = payload.get("sub")
        
        if user_id is None or username is None:
            raise credentials_exception
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ? AND username = ?", (user_id, username))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            raise credentials_exception
            
        return user_id
    except JWTError:
        raise credentials_exception

async def get_current_teacher(user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or user['role'] != 'teacher':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required",
        )
    return user_id

async def get_current_student(user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or user['role'] != 'student':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required",
        )
    return user_id

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

class CourseCreate(BaseModel):
    title: str
    description: str
    level: str = "Beginner"
    category: str
    duration: int = 60
    price: float = 0
    max_students: int = 10
    schedule: str

class WalletCreate(BaseModel):
    balance: float = 0.0

class PaymentCreate(BaseModel):
    amount: float
    description: str = "Deposit"

class ExamCreate(BaseModel):
    class_id: int
    title: str
    description: str
    questions: List[dict]
    duration: int = 60

class ExamSubmit(BaseModel):
    exam_id: int
    answers: List[dict]

class Token(BaseModel):
    access_token: str
    token_type: str

# مدل‌های جدید برای سیستم آموزشی
class LessonCreate(BaseModel):
    class_id: int
    title: str
    content_type: str = "text"
    content_url: Optional[str] = None
    duration: int = 0
    order_index: int = 0
    description: Optional[str] = None

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content_type: Optional[str] = None
    content_url: Optional[str] = None
    duration: Optional[int] = None
    order_index: Optional[int] = None
    description: Optional[str] = None
    is_published: Optional[bool] = None

class LessonProgressUpdate(BaseModel):
    lesson_id: int
    is_completed: bool = False
    progress_percentage: int = 0
    last_position: int = 0

class LessonProgressResponse(BaseModel):
    lesson_id: int
    is_completed: bool
    progress_percentage: int
    last_position: int
    completed_at: Optional[str] = None

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
        
        # جداول جدید برای سیستم آموزشی
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
        
        # اضافه کردن داده‌های تست اگر وجود ندارند
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        user_count = row_to_dict(result)['count'] if result else 0
        
        if user_count == 0:
            logger.info("Adding test data to database...")
            
            test_users = [
                ('admin@quran.com', get_password_hash('admin123'), 'admin', 'Admin User', 'admin@quran.com', '', 100, True),
                ('teacher1', get_password_hash('teacher123'), 'teacher', 'استاد احمد', 'teacher1@quran.com', 'Quran Recitation', 500, True),
                ('student1@quran.com', get_password_hash('student123'), 'student', 'دانشجو محمد', 'student1@quran.com', '', 50, True),
                ('student2@quran.com', get_password_hash('student123'), 'student', 'دانشجو فاطمه', 'student2@quran.com', '', 75, True)
            ]
            
            for user in test_users:
                try:
                    cursor.execute(
                        "INSERT INTO users (username, password, role, full_name, email, specialty, wallet_balance, approved) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
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
            
            cursor.execute("SELECT id FROM users WHERE username = 'teacher1'")
            teacher_result = cursor.fetchone()
            if teacher_result:
                teacher_id = row_to_dict(teacher_result)['id']
                
                test_classes = [
                    (teacher_id, 'Basic Quran Reading', 'Learn to read Quran from basics', 'Beginner', 'Recitation', 60, 0, 20, 'Mon, Wed, Fri 10:00-11:00'),
                    (teacher_id, 'Tajweed Fundamentals', 'Learn proper pronunciation rules', 'Intermediate', 'Tajweed', 60, 25, 15, 'Tue, Thu 14:00-15:00'),
                    (teacher_id, 'Advanced Recitation', 'Master Quran recitation', 'Advanced', 'Recitation', 90, 50, 10, 'Sat, Sun 09:00-10:30')
                ]
                
                class_ids = []
                for class_data in test_classes:
                    cursor.execute(
                        "INSERT INTO classes (teacher_id, title, description, level, category, duration, price, max_students, schedule) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        class_data
                    )
                    class_ids.append(cursor.lastrowid)
                
                # اضافه کردن دروس نمونه
                test_lessons = [
                    (class_ids[0], 'Introduction to Arabic Letters', 'text', None, 15, 1, 'Learn the basics of Arabic alphabet', True),
                    (class_ids[0], 'Basic Pronunciation', 'video', 'https://example.com/video1.mp4', 20, 2, 'Practice basic sounds', True),
                    (class_ids[0], 'Reading Practice', 'text', None, 25, 3, 'Practice reading simple words', True),
                    (class_ids[1], 'Tajweed Rules Overview', 'text', None, 30, 1, 'Introduction to Tajweed rules', True),
                    (class_ids[1], 'Practice Session 1', 'audio', 'https://example.com/audio1.mp3', 25, 2, 'First practice session', True),
                    (class_ids[2], 'Advanced Techniques', 'video', 'https://example.com/video2.mp4', 40, 1, 'Learn advanced recitation techniques', True)
                ]
                
                for lesson in test_lessons:
                    cursor.execute(
                        "INSERT INTO lessons (class_id, title, content_type, content_url, duration, order_index, description, is_published) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        lesson
                    )
                
                cursor.execute("SELECT id FROM users WHERE email = 'student1@quran.com'")
                student1_result = cursor.fetchone()
                cursor.execute("SELECT id FROM users WHERE email = 'student2@quran.com'")
                student2_result = cursor.fetchone()
                
                if student1_result and student2_result:
                    student1_id = row_to_dict(student1_result)['id']
                    student2_id = row_to_dict(student2_result)['id']
                    
                    test_enrollments = [
                        (student1_id, class_ids[0], 25),
                        (student1_id, class_ids[1], 50),
                        (student2_id, class_ids[0], 15)
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, full_name, wallet_balance FROM users")
        users = cursor.fetchall()
        conn.close()
        
        return {"users": rows_to_dict_list(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/reset-passwords")
async def reset_passwords():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        default_passwords = {
            "admin@quran.com": "admin123",
            "teacher1": "teacher123", 
            "student1@quran.com": "student123",
            "student2@quran.com": "student123"
        }
        
        updated_count = 0
        for username, password in default_passwords.items():
            hashed_password = get_password_hash(password)
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
        
        hashed_password = get_password_hash(student.password)
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
        
        hashed_password = get_password_hash(teacher.password)
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

@app.post("/api/login")
async def login(login_data: LoginRequest):
    try:
        logger.info(f"Login attempt: username={login_data.username}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (login_data.username, login_data.username)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(login_data.password, user['password']):
            user_dict = row_to_dict(user)
            
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"user_id": user_dict['id'], "sub": user_dict['username']},
                expires_delta=access_token_expires
            )
            
            logger.info(f"Login successful for user: {user_dict['username']}")
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user_dict['id'],
                "username": user_dict['username'],
                "role": user_dict['role']
            }
        else:
            logger.warning("Login failed: Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/me")
async def read_users_me(current_user: int = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (current_user,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            user_dict = row_to_dict(user)
            return {
                "id": user_dict['id'],
                "username": user_dict['username'],
                "full_name": user_dict['full_name'],
                "email": user_dict['email'],
                "role": user_dict['role'],
                "specialty": user_dict.get('specialty', ''),
                "wallet_balance": user_dict.get('wallet_balance', 0),
                "approved": bool(user_dict['approved'])
            }
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
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

@app.get("/my-courses")
async def get_my_courses(current_user: int = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, u.full_name as teacher_name, e.progress, e.enrolled_at
            FROM classes c
            JOIN enrollments e ON c.id = e.class_id
            JOIN users u ON c.teacher_id = u.id
            WHERE e.student_id = ? AND e.status = 'active'
        """, (current_user,))
        
        courses = cursor.fetchall()
        conn.close()
        
        return {"my_courses": rows_to_dict_list(courses)}
        
    except Exception as e:
        logger.error(f"Get my courses error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enroll/{class_id}")
async def enroll_student(class_id: int, current_user: int = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM classes WHERE id = ? AND status = 'active'", (class_id,))
        class_data = cursor.fetchone()
        
        if not class_data:
            raise HTTPException(status_code=404, detail="Class not found")
        
        cursor.execute("SELECT * FROM users WHERE id = ? AND role = 'student'", (current_user,))
        student = cursor.fetchone()
        
        if not student:
            raise HTTPException(status_code=403, detail="Only students can enroll in classes")
        
        cursor.execute(
            "SELECT * FROM enrollments WHERE student_id = ? AND class_id = ?",
            (current_user, class_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already enrolled in this class")
        
        cursor.execute(
            "INSERT INTO enrollments (student_id, class_id, status) VALUES (?, ?, 'active')",
            (current_user, class_id)
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
        
        cursor.execute("SELECT id, username, full_name, email, role, approved, wallet_balance FROM users")
        users = cursor.fetchall()
        
        conn.close()
        
        return {"users": rows_to_dict_list(users)}
        
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/teacher/courses")
async def create_course(
    course_data: CourseCreate, 
    current_user: int = Depends(get_current_teacher)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO classes (teacher_id, title, description, level, category, duration, price, max_students, schedule)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                current_user,
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

@app.get("/teacher/courses")
async def get_teacher_courses(current_user: int = Depends(get_current_teacher)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, COUNT(e.id) as enrolled_students
            FROM classes c
            LEFT JOIN enrollments e ON c.id = e.class_id
            WHERE c.teacher_id = ?
            GROUP BY c.id
        """, (current_user,))
        
        courses = cursor.fetchall()
        conn.close()
        
        return {"courses": rows_to_dict_list(courses)}
        
    except Exception as e:
        logger.error(f"Get teacher courses error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Wallet endpoints
@app.get("/wallet/balance")
async def get_wallet_balance(current_user: int = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT wallet_balance FROM users WHERE id = ?", (current_user,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"balance": result['wallet_balance']}
        return {"balance": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/wallet/deposit")
async def deposit_to_wallet(
    payment_data: PaymentCreate, 
    current_user: int = Depends(get_current_user)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET wallet_balance = wallet_balance + ? WHERE id = ?",
            (payment_data.amount, current_user)
        )
        
        cursor.execute(
            "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
            (current_user, payment_data.amount, 'deposit', payment_data.description)
        )
        
        cursor.execute("SELECT wallet_balance FROM users WHERE id = ?", (current_user,))
        new_balance = cursor.fetchone()['wallet_balance']
        
        conn.commit()
        conn.close()
        
        return {"success": True, "new_balance": new_balance}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wallet/transactions")
async def get_wallet_transactions(current_user: int = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (current_user,))
        
        transactions = cursor.fetchall()
        conn.close()
        
        return {"transactions": rows_to_dict_list(transactions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Exam endpoints
@app.post("/teacher/exams")
async def create_exam(
    exam_data: ExamCreate, 
    current_user: int = Depends(get_current_teacher)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO exams (class_id, teacher_id, title, description, questions, duration) VALUES (?, ?, ?, ?, ?, ?)",
            (
                exam_data.class_id,
                current_user,
                exam_data.title,
                exam_data.description,
                json.dumps(exam_data.questions),
                exam_data.duration
            )
        )
        
        exam_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {"success": True, "exam_id": exam_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/exams/{class_id}")
async def get_class_exams(class_id: int, current_user: int = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.*, u.full_name as teacher_name 
            FROM exams e 
            JOIN users u ON e.teacher_id = u.id 
            WHERE e.class_id = ?
        """, (class_id,))
        
        exams = cursor.fetchall()
        conn.close()
        
        return {"exams": rows_to_dict_list(exams)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/exams/{exam_id}/submit")
async def submit_exam(
    exam_id: int,
    exam_data: ExamSubmit,
    current_user: int = Depends(get_current_student)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate score (simple implementation)
        score = len([a for a in exam_data.answers if a.get('correct', False)])
        
        cursor.execute(
            "INSERT INTO exam_results (exam_id, student_id, score, answers) VALUES (?, ?, ?, ?)",
            (exam_id, current_user, score, json.dumps(exam_data.answers))
        )
        
        conn.commit()
        conn.close()
        
        return {"success": True, "score": score}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/exam-results")
async def get_exam_results(current_user: int = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT er.*, e.title as exam_name, c.title as class_name
            FROM exam_results er
            JOIN exams e ON er.exam_id = e.id
            JOIN classes c ON e.class_id = c.id
            WHERE er.student_id = ?
            ORDER BY er.completed_at DESC
        """, (current_user,))
        
        results = cursor.fetchall()
        conn.close()
        
        return {"results": rows_to_dict_list(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 📚 سیستم آموزشی جدید - APIهای مدیریت دروس
@app.post("/teacher/courses/{course_id}/lessons")
async def create_lesson(
    course_id: int, 
    lesson_data: LessonCreate, 
    current_user: int = Depends(get_current_teacher)
):
    try:
        # بررسی اینکه معلم صاحب دوره است
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM classes WHERE id = ? AND teacher_id = ?",
            (course_id, current_user)
        )
        course = cursor.fetchone()
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found or access denied")
        
        # ایجاد درس جدید
        cursor.execute(
            """
            INSERT INTO lessons (class_id, title, content_type, content_url, duration, order_index, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                course_id,
                lesson_data.title,
                lesson_data.content_type,
                lesson_data.content_url,
                lesson_data.duration,
                lesson_data.order_index,
                lesson_data.description
            )
        )
        
        lesson_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True, 
            "lesson_id": lesson_id, 
            "message": "Lesson created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating lesson: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/courses/{course_id}/lessons")
async def get_course_lessons(
    course_id: int,
    current_user: int = Depends(get_current_user)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # بررسی اینکه کاربر در دوره ثبت‌نام کرده یا معلم دوره است
        cursor.execute("""
            SELECT c.id, c.teacher_id, e.student_id 
            FROM classes c 
            LEFT JOIN enrollments e ON c.id = e.class_id AND e.student_id = ?
            WHERE c.id = ?
        """, (current_user, course_id))
        
        course_info = cursor.fetchone()
        if not course_info:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # اگر دانش‌آموز است و ثبت‌نام نکرده است
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user,))
        user_role = cursor.fetchone()['role']
        
        if user_role == 'student' and not course_info['student_id'] and course_info['teacher_id'] != current_user:
            raise HTTPException(status_code=403, detail="Not enrolled in this course")
        
        # دریافت دروس
        cursor.execute("""
            SELECT * FROM lessons 
            WHERE class_id = ? AND is_published = TRUE
            ORDER BY order_index
        """, (course_id,))
        
        lessons = rows_to_dict_list(cursor.fetchall())
        conn.close()
        
        return {"lessons": lessons}
        
    except Exception as e:
        logger.error(f"Error getting lessons: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/lessons/{lesson_id}")
async def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    current_user: int = Depends(get_current_teacher)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # بررسی مالکیت درس
        cursor.execute("""
            SELECT l.id, c.teacher_id 
            FROM lessons l 
            JOIN classes c ON l.class_id = c.id 
            WHERE l.id = ?
        """, (lesson_id,))
        
        lesson_info = cursor.fetchone()
        if not lesson_info or lesson_info['teacher_id'] != current_user:
            raise HTTPException(status_code=404, detail="Lesson not found or access denied")
        
        # بروزرسانی درس
        update_fields = []
        update_values = []
        
        if lesson_data.title is not None:
            update_fields.append("title = ?")
            update_values.append(lesson_data.title)
        if lesson_data.content_type is not None:
            update_fields.append("content_type = ?")
            update_values.append(lesson_data.content_type)
        if lesson_data.content_url is not None:
            update_fields.append("content_url = ?")
            update_values.append(lesson_data.content_url)
        if lesson_data.duration is not None:
            update_fields.append("duration = ?")
            update_values.append(lesson_data.duration)
        if lesson_data.order_index is not None:
            update_fields.append("order_index = ?")
            update_values.append(lesson_data.order_index)
        if lesson_data.description is not None:
            update_fields.append("description = ?")
            update_values.append(lesson_data.description)
        if lesson_data.is_published is not None:
            update_fields.append("is_published = ?")
            update_values.append(lesson_data.is_published)
        
        if update_fields:
            update_values.append(lesson_id)
            cursor.execute(
                f"UPDATE lessons SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                update_values
            )
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Lesson updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating lesson: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/lessons/{lesson_id}")
async def delete_lesson(
    lesson_id: int,
    current_user: int = Depends(get_current_teacher)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # بررسی مالکیت درس
        cursor.execute("""
            SELECT l.id, c.teacher_id 
            FROM lessons l 
            JOIN classes c ON l.class_id = c.id 
            WHERE l.id = ?
        """, (lesson_id,))
        
        lesson_info = cursor.fetchone()
        if not lesson_info or lesson_info['teacher_id'] != current_user:
            raise HTTPException(status_code=404, detail="Lesson not found or access denied")
        
        cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Lesson deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting lesson: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons/{lesson_id}")
async def get_lesson(
    lesson_id: int,
    current_user: int = Depends(get_current_user)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.*, c.title as course_title
            FROM lessons l
            JOIN classes c ON l.class_id = c.id
            WHERE l.id = ? AND l.is_published = TRUE
        """, (lesson_id,))
        
        lesson = cursor.fetchone()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # بررسی دسترسی
        cursor.execute("""
            SELECT role FROM users WHERE id = ?
        """, (current_user,))
        user_role = cursor.fetchone()['role']
        
        if user_role == 'student':
            cursor.execute("""
                SELECT student_id FROM enrollments 
                WHERE class_id = ? AND student_id = ?
            """, (lesson['class_id'], current_user))
            if not cursor.fetchone():
                raise HTTPException(status_code=403, detail="Not enrolled in this course")
        
        conn.close()
        return {"lesson": row_to_dict(lesson)}
        
    except Exception as e:
        logger.error(f"Error getting lesson: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 📊 سیستم ردیابی پیشرفت
@app.post("/progress/lesson")
async def update_lesson_progress(
    progress_data: LessonProgressUpdate,
    current_user: int = Depends(get_current_student)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # بررسی اینکه درس وجود دارد و دانش‌آموز در دوره ثبت‌نام کرده
        cursor.execute("""
            SELECT l.id, l.class_id, e.student_id 
            FROM lessons l 
            JOIN classes c ON l.class_id = c.id 
            LEFT JOIN enrollments e ON c.id = e.class_id AND e.student_id = ?
            WHERE l.id = ?
        """, (current_user, progress_data.lesson_id))
        
        lesson_info = cursor.fetchone()
        if not lesson_info or not lesson_info['student_id']:
            raise HTTPException(status_code=404, detail="Lesson not found or not enrolled")
        
        # بروزرسانی یا ایجاد رکورد پیشرفت
        cursor.execute("""
            INSERT OR REPLACE INTO lesson_progress 
            (student_id, lesson_id, class_id, is_completed, progress_percentage, last_position, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            current_user,
            progress_data.lesson_id,
            lesson_info['class_id'],
            progress_data.is_completed,
            progress_data.progress_percentage,
            progress_data.last_position
        ))
        
        # اگر درس کامل شده است، تاریخ تکمیل را تنظیم کن
        if progress_data.is_completed:
            cursor.execute("""
                UPDATE lesson_progress 
                SET completed_at = CURRENT_TIMESTAMP 
                WHERE student_id = ? AND lesson_id = ?
            """, (current_user, progress_data.lesson_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Progress updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress/course/{course_id}")
async def get_course_progress(
    course_id: int,
    current_user: int = Depends(get_current_user)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # دریافت اطلاعات پیشرفت برای دوره
        cursor.execute("""
            SELECT l.id as lesson_id, l.title, lp.is_completed, lp.progress_percentage,
                   lp.last_position, lp.completed_at
            FROM lessons l
            LEFT JOIN lesson_progress lp ON l.id = lp.lesson_id AND lp.student_id = ?
            WHERE l.class_id = ? AND l.is_published = TRUE
            ORDER BY l.order_index
        """, (current_user, course_id))
        
        progress_data = rows_to_dict_list(cursor.fetchall())
        
        # محاسبه پیشرفت کلی دوره
        total_lessons = len(progress_data)
        completed_lessons = sum(1 for lesson in progress_data if lesson['is_completed'])
        overall_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        conn.close()
        
        return {
            "progress": progress_data,
            "overall_progress": round(overall_progress, 2),
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons
        }
        
    except Exception as e:
        logger.error(f"Error getting course progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teacher/courses/{course_id}/progress")
async def get_course_progress_for_teacher(
    course_id: int,
    current_user: int = Depends(get_current_teacher)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # بررسی مالکیت دوره
        cursor.execute("SELECT id FROM classes WHERE id = ? AND teacher_id = ?", (course_id, current_user))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Course not found or access denied")
        
        # دریافت پیشرفت همه دانش‌آموزان
        cursor.execute("""
            SELECT u.id as student_id, u.full_name, 
                   COUNT(l.id) as total_lessons,
                   COUNT(CASE WHEN lp.is_completed THEN 1 END) as completed_lessons,
                   ROUND(COUNT(CASE WHEN lp.is_completed THEN 1 END) * 100.0 / COUNT(l.id), 2) as progress_percentage
            FROM users u
            JOIN enrollments e ON u.id = e.student_id
            JOIN lessons l ON e.class_id = l.class_id AND l.is_published = TRUE
            LEFT JOIN lesson_progress lp ON l.id = lp.lesson_id AND lp.student_id = u.id
            WHERE e.class_id = ?
            GROUP BY u.id, u.full_name
            ORDER BY u.full_name
        """, (course_id,))
        
        student_progress = rows_to_dict_list(cursor.fetchall())
        conn.close()
        
        return {"student_progress": student_progress}
        
    except Exception as e:
        logger.error(f"Error getting teacher course progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
