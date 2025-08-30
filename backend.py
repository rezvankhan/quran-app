from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
import os
import sqlite3

# برای توسعه محلی
load_dotenv()

# تنظیمات دیتابیس - سازگار با Render
def get_db_connection():
    conn = sqlite3.connect('quran_db.sqlite3')
    conn.row_factory = sqlite3.Row
    
    # ایجاد خودکار جدول اگر وجود ندارد
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            full_name TEXT,
            grade TEXT,
            specialty TEXT,
            approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # اضافه کردن فیلدهای جدید اگر وجود ندارند
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    except sqlite3.OperationalError:
        pass  # اگر فیلد already exists
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN grade TEXT")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN specialty TEXT")
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    
    return conn

app = FastAPI(title="Quran API", version="1.0.0")

# تنظیمات CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# رمزنگاری پسورد
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-key-change-in-production")
ALGORITHM = "HS256"

# مدل‌های ورودی
class User(BaseModel):
    username: str
    password: str

class StudentRegister(BaseModel):
    username: str
    password: str
    full_name: str
    grade: str

class TeacherRegister(BaseModel):
    username: str
    password: str
    full_name: str
    specialty: str

class Token(BaseModel):
    access_token: str
    token_type: str

# تابع ایجاد توکن
def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

# مسیر سلامت سرور
@app.get("/")
async def root():
    return {"message": "Quran API is running", "status": "healthy"}

# مسیر ثبت‌نام دانش‌آموز
@app.post("/register-student", response_model=dict)
async def register_student(student: StudentRegister):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # بررسی وجود کاربر
        cursor.execute("SELECT id FROM users WHERE username = ?", (student.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists")

        # هش کردن رمز عبور
        hashed_password = pwd_context.hash(student.password)
        
        # ثبت دانش‌آموز جدید
        cursor.execute(
            "INSERT INTO users (username, password, role, full_name, grade, approved) VALUES (?, ?, ?, ?, ?, ?)",
            (student.username, hashed_password, "student", student.full_name, student.grade, True)
        )
        
        conn.commit()
        return {"message": "Student registered successfully", "status": "success"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

# مسیر ثبت‌نام معلم
@app.post("/register-teacher", response_model=dict)
async def register_teacher(teacher: TeacherRegister):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # بررسی وجود کاربر
        cursor.execute("SELECT id FROM users WHERE username = ?", (teacher.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists")

        # هش کردن رمز عبور
        hashed_password = pwd_context.hash(teacher.password)
        
        # ثبت معلم جدید (نیاز به تایید admin)
        cursor.execute(
            "INSERT INTO users (username, password, role, full_name, specialty, approved) VALUES (?, ?, ?, ?, ?, ?)",
            (teacher.username, hashed_password, "teacher", teacher.full_name, teacher.specialty, False)
        )
        
        conn.commit()
        return {"message": "Teacher registered successfully. Waiting for admin approval.", "status": "success"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

# مسیر ورود
@app.post("/login", response_model=Token)
async def login(user: User):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # پیدا کردن کاربر
        cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
        db_user = cursor.fetchone()

        if not db_user or not pwd_context.verify(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # بررسی تایید حساب معلم
        if db_user["role"] == "teacher" and not db_user["approved"]:
            raise HTTPException(status_code=401, detail="Teacher account not approved yet")

        # ایجاد توکن
        access_token = create_access_token(user.username)
        
        return {"access_token": access_token, "token_type": "bearer"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

# مسیر دریافت اطلاعات کاربر
@app.get("/users/me")
async def read_users_me(token: str = Depends(lambda: None)):
    conn = None
    try:
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, role, full_name, grade, specialty, approved FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "id": user[0],
            "username": user[1],
            "role": user[2],
            "full_name": user[3],
            "grade": user[4],
            "specialty": user[5],
            "approved": user[6]
        }
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

# مسیر دریافت معلمان در انتظار تایید
@app.get("/pending-teachers")
async def get_pending_teachers():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, full_name, specialty, created_at FROM users WHERE role = 'teacher' AND approved = FALSE")
        teachers = cursor.fetchall()
        
        return [dict(teacher) for teacher in teachers]
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

# مسیر تایید معلم
@app.post("/approve-teacher/{teacher_id}")
async def approve_teacher(teacher_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET approved = TRUE WHERE id = ? AND role = 'teacher'", (teacher_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        conn.commit()
        return {"message": "Teacher approved successfully", "status": "success"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

# برای اجرای محلی
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)