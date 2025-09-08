from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
import sqlite3
import os

# ================== تنظیمات ==================
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DB_FILE = "quran_app.db"

# فعال‌سازی CORS برای اتصال از سمت اپلیکیشن
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== دیتابیس ==================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT CHECK(role IN ('teacher','student','admin')) NOT NULL,
                        approved BOOLEAN DEFAULT 0
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS classes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        teacher_id INTEGER,
                        FOREIGN KEY (teacher_id) REFERENCES users (id)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS exams (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        class_id INTEGER,
                        question TEXT,
                        correct_answer TEXT,
                        FOREIGN KEY (class_id) REFERENCES classes (id)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS wallets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        balance REAL DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )''')

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# ================== مدل‌ها ==================
class RegisterUser(BaseModel):
    username: str
    password: str
    role: str  # teacher, student, admin


class LoginUser(BaseModel):
    username: str
    password: str


# ================== مسیرها ==================
@app.post("/register")
def register_user(user: RegisterUser):
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = pwd_context.hash(user.password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role, approved) VALUES (?, ?, ?, ?)",
            (user.username, hashed_password, user.role, 0 if user.role == "teacher" else 1),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()

    return {"msg": "User registered successfully"}


@app.post("/login")
def login_user(user: LoginUser):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    db_user = cursor.fetchone()
    conn.close()

    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if db_user["role"] == "teacher" and not db_user["approved"]:
        raise HTTPException(status_code=403, detail="Teacher not approved yet")

    return {"msg": "Login successful", "role": db_user["role"]}


@app.get("/approve_teacher/{teacher_id}")
def approve_teacher(teacher_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET approved = 1 WHERE id = ? AND role = 'teacher'", (teacher_id,))
    conn.commit()
    conn.close()

    return {"msg": f"Teacher {teacher_id} approved"}


# ================== اجرای مستقیم ==================
if __name__ == "__main__":
    import uvicorn

    init_db()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
