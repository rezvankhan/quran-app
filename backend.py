from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه برای imports
sys.path.append(str(Path(__file__).parent))

# Import با handling خطا برای Render
try:
    from creat_tables import get_db_connection
except ImportError:
    # برای Render
    try:
        from .creat_tables import get_db_connection
    except ImportError:
        # Fallback نهایی
        def get_db_connection():
            # این تابع باید با PostgreSQL کار کند
            import psycopg2
            from urllib.parse import urlparse
            
            DATABASE_URL = os.getenv('DATABASE_URL')
            if DATABASE_URL:
                parsed_url = urlparse(DATABASE_URL)
                conn = psycopg2.connect(
                    host=parsed_url.hostname,
                    database=parsed_url.path[1:],
                    user=parsed_url.username,
                    password=parsed_url.password,
                    port=parsed_url.port
                )
                return conn
            else:
                # Fallback برای توسعه محلی
                import sqlite3
                conn = sqlite3.connect('quran_db.sqlite3')
                conn.row_factory = sqlite3.Row
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

# مسیر ثبت‌نام
@app.post("/register", response_model=dict)
async def register(user: User):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # بررسی وجود کاربر
        cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists")

        # هش کردن رمز عبور
        hashed_password = pwd_context.hash(user.password)
        
        # ثبت کاربر جدید
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (user.username, hashed_password)
        )
        
        conn.commit()
        return {"message": "User registered successfully", "status": "success"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# مسیر ورود
@app.post("/login", response_model=Token)
async def login(user: User):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # پیدا کردن کاربر
        cursor.execute("SELECT * FROM users WHERE username = %s", (user.username,))
        db_user = cursor.fetchone()

        if not db_user or not pwd_context.verify(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # ایجاد توکن
        access_token = create_access_token(user.username)
        
        return {"access_token": access_token, "token_type": "bearer"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# مسیر دریافت اطلاعات کاربر
@app.get("/users/me")
async def read_users_me(token: str = Depends(lambda: None)):
    conn = None
    cursor = None
    try:
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "id": user[0],
            "username": user[1],
            "role": user[2]
        }
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:

            conn.close()

            conn.close()

