# backend.py - کامل با دیباگ
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

# تابع hash کردن password
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ایجاد جداول
def init_db():
    try:
        conn = get_db_connection()
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
        logger.info("Database tables created successfully")
        
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
    return {"message": "Quran App API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/register/student")
async def register_student(student: StudentRegister):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(student.password)
        logger.info(f"Registering student: {student.email}, password_hash: {hashed_password}")
        
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
        logger.info(f"Registering teacher: {teacher.username}, password_hash: {hashed_password}")
        
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
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(login_data.password)
        logger.info(f"Login attempt: username={login_data.username}, password_hash={hashed_password}")
        
        cursor.execute(
            "SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?",
            (login_data.username, login_data.username, hashed_password)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            logger.info(f"Login successful: {user['username']}")
            return {
                "success": True,
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "full_name": user['full_name'],
                    "email": user['email'],
                    "role": user['role'],
                    "specialty": user.get('specialty', ''),
                    "approved": bool(user['approved'])
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
        
        return {"courses": [dict(course) for course in courses]}
        
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
        
        return {"my_courses": [dict(course) for course in courses]}
        
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
        
        return {"users": [dict(user) for user in users]}
        
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
