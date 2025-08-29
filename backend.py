# main.py (Backend - FastAPI)
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from dotenv import load_dotenv
import sqlite3
import os
from typing import List, Optional
import uuid

load_dotenv()

def get_db_connection():
    conn = sqlite3.connect('quran_db.sqlite3')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # ایجاد جداول
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level TEXT NOT NULL,
            teacher_id INTEGER,
            schedule_time TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS class_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            student_id INTEGER,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id),
            FOREIGN KEY (student_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            class_id INTEGER,
            teacher_id INTEGER,
            duration_minutes INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id),
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            class_id INTEGER,
            message_text TEXT,
            file_path TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id),
            FOREIGN KEY (class_id) REFERENCES classes (id)
        );
    """)
    conn.commit()
    return conn

app = FastAPI(title="Quran Education System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-key-change-in-production")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# مدل‌های جدید
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "student"

class ClassCreate(BaseModel):
    name: str
    level: str
    schedule_time: str

class ExamCreate(BaseModel):
    title: str
    description: str
    class_id: int
    duration_minutes: int

class MessageCreate(BaseModel):
    receiver_id: Optional[int] = None
    class_id: Optional[int] = None
    message_text: str

def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# endpointهای جدید
@app.post("/register-teacher")
async def register_teacher(user: UserCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can register teachers")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        hashed_password = pwd_context.hash(user.password)
        cursor.execute(
            "INSERT INTO users (username, password, role, approved) VALUES (?, ?, ?, ?)",
            (user.username, hashed_password, "teacher", False)
        )
        conn.commit()
        return {"message": "Teacher registered successfully, waiting for approval"}
    finally:
        conn.close()

@app.get("/pending-teachers")
async def get_pending_teachers(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view pending teachers")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, created_at FROM users WHERE role = 'teacher' AND approved = FALSE")
        teachers = cursor.fetchall()
        return [dict(teacher) for teacher in teachers]
    finally:
        conn.close()

@app.post("/approve-teacher/{teacher_id}")
async def approve_teacher(teacher_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can approve teachers")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET approved = TRUE WHERE id = ? AND role = 'teacher'", (teacher_id,))
        conn.commit()
        return {"message": "Teacher approved successfully"}
    finally:
        conn.close()

@app.post("/create-class")
async def create_class(class_data: ClassCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher" or not current_user["approved"]:
        raise HTTPException(status_code=403, detail="Only approved teachers can create classes")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO classes (name, level, teacher_id, schedule_time) VALUES (?, ?, ?, ?)",
            (class_data.name, class_data.level, current_user["id"], class_data.schedule_time)
        )
        conn.commit()
        return {"message": "Class created successfully"}
    finally:
        conn.close()

@app.post("/create-exam")
async def create_exam(exam_data: ExamCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher" or not current_user["approved"]:
        raise HTTPException(status_code=403, detail="Only approved teachers can create exams")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO exams (title, description, class_id, teacher_id, duration_minutes) VALUES (?, ?, ?, ?, ?)",
            (exam_data.title, exam_data.description, exam_data.class_id, current_user["id"], exam_data.duration_minutes)
        )
        conn.commit()
        return {"message": "Exam created successfully"}
    finally:
        conn.close()

@app.post("/send-message")
async def send_message(message: MessageCreate, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (sender_id, receiver_id, class_id, message_text) VALUES (?, ?, ?, ?)",
            (current_user["id"], message.receiver_id, message.class_id, message.message_text)
        )
        conn.commit()
        return {"message": "Message sent successfully"}
    finally:
        conn.close()

@app.get("/class-messages/{class_id}")
async def get_class_messages(class_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, u.username as sender_name 
            FROM messages m 
            JOIN users u ON m.sender_id = u.id 
            WHERE m.class_id = ? 
            ORDER BY m.sent_at
        """, (class_id,))
        messages = cursor.fetchall()
        return [dict(msg) for msg in messages]
    finally:
        conn.close()
