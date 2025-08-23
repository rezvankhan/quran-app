from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from creat_tables import get_db_connection
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Quran API", version="1.0.0")

# تنظیمات CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # برای توسعه - در production محدود کنید
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# رمزنگاری پسورد
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-key")
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
    expire = datetime.utcnow() + timedelta(days=30)  # 30 روز
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

# مسیر سلامت سرور
@app.get("/")
async def root():
    return {"message": "Quran API is running", "status": "healthy"}

# مسیر ثبت‌نام
@app.post("/register", response_model=dict)
async def register(user: User):
    try:
        with get_db_connection("quran_db") as (cursor, conn):
            # بررسی وجود کاربر
            cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="نام کاربری already exists")

            # هش کردن رمز عبور
            hashed_password = pwd_context.hash(user.password)
            
            # ثبت کاربر جدید
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (user.username, hashed_password)
            )
            
            return {"message": "User registered successfully", "status": "success"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطای سرور: {str(e)}")

# مسیر ورود
@app.post("/login", response_model=Token)
async def login(user: User):
    try:
        with get_db_connection("quran_db") as (cursor, conn):
            # پیدا کردن کاربر
            cursor.execute("SELECT * FROM users WHERE username = %s", (user.username,))
            db_user = cursor.fetchone()

            if not db_user or not pwd_context.verify(user.password, db_user["password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            # ایجاد توکن
            access_token = create_access_token(user.username)
            
            return {"access_token": access_token, "token_type": "bearer"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطای سرور: {str(e)}")

# مسیر دریافت اطلاعات کاربر
@app.get("/users/me")
async def read_users_me(token: str = Depends(lambda: None)):
    try:
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        with get_db_connection("quran_db") as (cursor, conn):
            cursor.execute("SELECT id, username, role FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
                
            return user
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطای سرور: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)