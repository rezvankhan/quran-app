from fastapi import FastAPI, HTTPException, Depends, WebSocket, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
import os
import sqlite3
import logging
import aiofiles
import json
from typing import List, Optional

# تنظیمات logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# برای توسعه محلی
load_dotenv()

# تنظیمات دیتابیس - سازگار با Render
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'quran_db.sqlite3')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # ایجاد خودکار جدول اگر وجود ندارد
    cursor = conn.cursor()
    
    # جدول users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            full_name TEXT,
            email TEXT,
            grade TEXT,
            specialty TEXT,
            approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول classes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            teacher_id INTEGER,
            class_type TEXT,
            level TEXT DEFAULT 'beginner',
            max_students INTEGER DEFAULT 10,
            price REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    """)
    
    # جدول class_students
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER,
            student_id INTEGER,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id),
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    """)
    
    # جدول exams
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            teacher_id INTEGER,
            class_id INTEGER,
            questions TEXT,  # JSON string
            duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id),
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    """)
    
    # جدول exam_results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER,
            student_id INTEGER,
            score REAL,
            answers TEXT,  # JSON string
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (exam_id) REFERENCES exams (id),
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    """)
    
    # جدول permissions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            can_teach BOOLEAN DEFAULT FALSE,
            can_manage_classes BOOLEAN DEFAULT FALSE,
            can_manage_users BOOLEAN DEFAULT FALSE,
            can_manage_content BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # جدول payments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            currency TEXT DEFAULT 'USDT',
            status TEXT DEFAULT 'pending',
            invoice_id TEXT,
            class_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    """)
    
    conn.commit()
    return conn

app = FastAPI(title="Quran API", version="2.0.0")

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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# مدل‌های ورودی
class User(BaseModel):
    username: str
    password: str

class StudentRegister(BaseModel):
    username: str
    password: str
    full_name: str
    email: str = None
    grade: str = None

class TeacherRegister(BaseModel):
    username: str
    password: str
    full_name: str
    email: str = None
    specialty: str = None

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str = None
    full_name: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ClassCreate(BaseModel):
    title: str
    description: str
    class_type: str
    level: str = "beginner"
    max_students: int = 10
    price: float = 0.0

class ExamCreate(BaseModel):
    title: str
    description: str
    class_id: int
    questions: List[dict]
    duration: int

class ExamSubmit(BaseModel):
    answers: List[dict]
    exam_id: int

class PaymentCreate(BaseModel):
    amount: float
    currency: str = "USDT"
    class_id: int

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][user_id] = websocket
    
    def disconnect(self, room_id: str, user_id: str):
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            del self.active_connections[room_id][user_id]
    
    async def broadcast(self, message: dict, room_id: str, sender_id: str):
        if room_id in self.active_connections:
            for user_id, websocket in self.active_connections[room_id].items():
                if user_id != sender_id:
                    await websocket.send_json(message)

manager = ConnectionManager()

# تابع ایجاد توکن
def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

# تابع گرفتن کاربر فعلی
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, full_name, email, grade, specialty, approved FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "id": user[0],
            "username": user[1],
            "role": user[2],
            "full_name": user[3],
            "email": user[4],
            "grade": user[5],
            "specialty": user[6],
            "approved": user[7]
        }
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# مسیر سلامت سرور
@app.get("/")
async def root():
    return {"message": "Quran API is running", "status": "healthy"}

# مسیر ریست دیتابیس (برای توسعه)
@app.post("/reset-db")
async def reset_database():
    try:
        import os
        db_path = os.path.join(os.path.dirname(__file__), 'quran_db.sqlite3')
        
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info("Old database deleted")
        
        conn = get_db_connection()
        conn.close()
        
        return {"message": "Database reset successfully", "status": "success"}
        
    except Exception as e:
        logger.error(f"Reset error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Reset error: {str(e)}")

# مسیرهای کاربران
@app.post("/register-student", response_model=dict)
async def register_student(student: StudentRegister):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (student.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists")

        hashed_password = pwd_context.hash(student.password)
        
        cursor.execute(
            "INSERT INTO users (username, password, role, full_name, email, grade, approved) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (student.username, hashed_password, "student", student.full_name, student.email, student.grade, True)
        )
        
        conn.commit()
        return {"message": "Student registered successfully", "status": "success"}
            
    except Exception as e:
        logger.error(f"Student registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.post("/register-teacher", response_model=dict)
async def register_teacher(teacher: TeacherRegister):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (teacher.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists")

        hashed_password = pwd_context.hash(teacher.password)
        
        cursor.execute(
            "INSERT INTO users (username, password, role, full_name, email, specialty, approved) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (teacher.username, hashed_password, "teacher", teacher.full_name, teacher.email, teacher.specialty, False)
        )
        
        conn.commit()
        return {"message": "Teacher registered successfully. Waiting for admin approval.", "status": "success"}
            
    except Exception as e:
        logger.error(f"Teacher registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.post("/login", response_model=Token)
async def login(user: User):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
        db_user = cursor.fetchone()

        if not db_user or not pwd_context.verify(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if db_user["role"] == "teacher" and not db_user["approved"]:
            raise HTTPException(status_code=401, detail="Teacher account not approved yet")

        access_token = create_access_token(user.username)
        
        return {"access_token": access_token, "token_type": "bearer"}
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

# مسیرهای مدیریتی
@app.get("/admin/teachers/pending")
async def get_pending_teachers(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can access")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, email, specialty, created_at FROM users WHERE role = 'teacher' AND approved = FALSE")
    teachers = cursor.fetchall()
    conn.close()
    
    return [dict(teacher) for teacher in teachers]

@app.post("/admin/teachers/{teacher_id}/approve")
async def approve_teacher(teacher_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can access")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET approved = TRUE WHERE id = ? AND role = 'teacher'", (teacher_id,))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Teacher approved successfully", "status": "success"}

# مسیرهای کلاس
@app.post("/classes", response_model=dict)
async def create_class(class_data: ClassCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher" or not current_user["approved"]:
        raise HTTPException(status_code=403, detail="Only approved teachers can create classes")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO classes (title, description, teacher_id, class_type, level, max_students, price) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (class_data.title, class_data.description, current_user["id"], class_data.class_type, class_data.level, class_data.max_students, class_data.price)
        )
        
        conn.commit()
        return {"message": "Class created successfully", "status": "success", "class_id": cursor.lastrowid}
            
    except Exception as e:
        logger.error(f"Class creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.get("/classes")
async def get_classes():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, u.full_name as teacher_name 
            FROM classes c 
            JOIN users u ON c.teacher_id = u.id 
            WHERE u.approved = TRUE
        """)
        classes = cursor.fetchall()
        
        return [dict(cls) for cls in classes]
            
    except Exception as e:
        logger.error(f"Get classes error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

# مسیرهای WebSocket برای چت و کلاس آنلاین
@app.websocket("/ws/chat/{room_id}")
async def websocket_chat_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    await manager.connect(websocket, f"chat_{room_id}", user_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast({
                "type": "chat",
                "user_id": user_id,
                "message": data["message"],
                "timestamp": datetime.utcnow().isoformat()
            }, f"chat_{room_id}", user_id)
    except:
        manager.disconnect(f"chat_{room_id}", user_id)

@app.websocket("/ws/class/{class_id}")
async def websocket_class_endpoint(websocket: WebSocket, class_id: str, user_id: str):
    await manager.connect(websocket, f"class_{class_id}", user_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast({
                "type": "class",
                "user_id": user_id,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }, f"class_{class_id}", user_id)
    except:
        manager.disconnect(f"class_{class_id}", user_id)

# مسیرهای آپلود فایل
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        file_path = os.path.join(UPLOAD_DIR, f"{current_user['id']}_{file.filename}")
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        return {"filename": file.filename, "path": file_path, "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")

# مسیرهای پرداخت
@app.post("/payment/create")
async def create_payment(payment_data: PaymentCreate, current_user: dict = Depends(get_current_user)):
    # در اینجا باید با API کیف پول رمزاری ارتباط برقرار کنید
    # این یک نمونه ساده است
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        invoice_id = f"inv_{current_user['id']}_{int(datetime.utcnow().timestamp())}"
        
        cursor.execute(
            "INSERT INTO payments (user_id, amount, currency, invoice_id, class_id, status) VALUES (?, ?, ?, ?, ?, ?)",
            (current_user["id"], payment_data.amount, payment_data.currency, invoice_id, payment_data.class_id, "pending")
        )
        
        conn.commit()
        
        return {
            "message": "Payment invoice created",
            "invoice_id": invoice_id,
            "amount": payment_data.amount,
            "currency": payment_data.currency,
            "payment_url": f"https://crypto-payment-gateway.com/pay/{invoice_id}"
        }
            
    except Exception as e:
        logger.error(f"Payment creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

# مسیرهای امتحان
@app.post("/exams")
async def create_exam(exam_data: ExamCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher" or not current_user["approved"]:
        raise HTTPException(status_code=403, detail="Only approved teachers can create exams")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        questions_json = json.dumps(exam_data.questions)
        
        cursor.execute(
            "INSERT INTO exams (title, description, teacher_id, class_id, questions, duration) VALUES (?, ?, ?, ?, ?, ?)",
            (exam_data.title, exam_data.description, current_user["id"], exam_data.class_id, questions_json, exam_data.duration)
        )
        
        conn.commit()
        return {"message": "Exam created successfully", "status": "success", "exam_id": cursor.lastrowid}
            
    except Exception as e:
        logger.error(f"Exam creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.post("/exams/{exam_id}/submit")
async def submit_exam(exam_id: int, exam_data: ExamSubmit, current_user: dict = Depends(get_current_user)):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # محاسبه نمره (این یک نمونه ساده است)
        score = calculate_score(exam_id, exam_data.answers)
        
        answers_json = json.dumps(exam_data.answers)
        
        cursor.execute(
            "INSERT INTO exam_results (exam_id, student_id, score, answers) VALUES (?, ?, ?, ?)",
            (exam_id, current_user["id"], score, answers_json)
        )
        
        conn.commit()
        return {"message": "Exam submitted successfully", "score": score, "status": "success"}
            
    except Exception as e:
        logger.error(f"Exam submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        if conn:
            conn.close()

def calculate_score(exam_id: int, answers: List[dict]) -> float:
    # این تابع باید منطق محاسبه نمره را پیاده‌سازی کند
    # این یک نمونه ساده است
    return 85.5  # نمره نمونه

# برای اجرای محلی
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
