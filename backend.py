from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
import os
import sqlite3
import logging

# تنظیمات logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# برای توسعه محلی
load_dotenv()

# تنظیمات دیتابیس - سازگار با Render
def get_db_connection():
    # استفاده از path مطلق برای Render
    db_path = os.path.join(os.path.dirname(__file__), 'quran_db.sqlite3')
    conn = sqlite3.connect(db_path)
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

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    full_name: str
    role: str = "student"

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

# مسیر ثبت‌نام یکپارچه
@app.post("/register", response_model=dict)
async def register(user: RegisterRequest):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # بررسی وجود کاربر
        cursor.execute("SELECT id FROM users WHERE username = ?", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists")

        # هش کردن رمز عبور
        hashed_password = pwd_context.hash(user.password)
        
        # ثبت کاربر جدید
        approved = user.role == "student"  # دانش‌آموزان به طور خودکار تایید می‌شوند
        cursor.execute(
            "INSERT INTO users (username, password, role, full_name, approved) VALUES (?, ?, ?, ?, ?)",
            (user.username, hashed_password, user.role, user.full_name, approved)
        )
        
        conn.commit()
        
        message = "Registration successful"
        if user.role == "teacher":
            message += ". Waiting for admin approval."
            
        return {"message": message, "status": "success"}
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
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
        logger.error(f"Login error: {str(e)}")
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
        logger.error(f"User me error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()
