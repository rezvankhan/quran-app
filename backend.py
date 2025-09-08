# backend.py - کامل با ثبت نام معلم
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
import logging
import hashlib
import os
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager
import json

# تنظیمات logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    conn = sqlite3.connect('quran_db.sqlite3')
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
                approved BOOLEAN DEFAULT FALSE,
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
    return {"message": "Quran App API is running", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/register/student")
async def register_student(student: StudentRegister):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(student.password)
        
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register/teacher")
async def register_teacher(teacher: TeacherRegister):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(teacher.password)
        
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(login_data: LoginRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(login_data.password)
        
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (login_data.username, hashed_password)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "success": True,
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "full_name": user['full_name'],
                    "email": user['email'],
                    "role": user['role'],
                    "approved": bool(user['approved'])
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
