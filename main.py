

from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel 
import mysql.connector

app = FastAPI()

#MySQL (XAMPP)

conn = mysql.connector.connect( 
    host="localhost", 
    user="root", password="", 
    database="quran_db" ) 
cursor = conn.cursor(dictionary=True)

#-------- مدل‌های Pydantic --------

class User(BaseModel): 
    username: str 
    password: str 
    role: str # 'student', 'teacher', 'admin'

#-------- ثبت‌نام کاربر --------

@app.post("/register") 
def register(user: User):
    cursor.execute("SELECT * FROM users WHERE username=%s", (user.username,))
    if cursor.fetchone():    raise HTTPException(status_code=400, detail="نام کاربری قبلاً ثبت شده است")
    cursor.execute( "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (user.username, user.password, user.role) ) 
    conn.commit() 
    return {"message": "ثبت‌نام با موفقیت انجام شد"}

#-------- ورود کاربر --------

@app.post("/login") 
def login(user: User): 
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (user.username, user.password)) 
    result = cursor.fetchone() 
    if result:return {"message": "ورود موفق", "user": result}
raise HTTPException(status_code=401, detail="نام کاربری یا رمز عبور اشتباه است")

#-------- تایید استاد --------

@app.post("/approve_teacher/{user_id}") 
def approve_teacher(user_id: int):
    cursor.execute("UPDATE users SET approved=TRUE WHERE id=%s AND role='teacher'",(user_id,)) 
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="استاد یافت نشد") 
    conn.commit() 
    return {"message": "استاد تایید شد"}




from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel 
import mysql.connector

app = FastAPI()

#MySQL (XAMPP)

conn = mysql.connector.connect( 
    host="localhost", 
    user="root", password="", 
    database="quran_db" ) 
cursor = conn.cursor(dictionary=True)

#-------- مدل‌های Pydantic --------

class User(BaseModel): 
    username: str 
    password: str 
    role: str # 'student', 'teacher', 'admin'

#-------- ثبت‌نام کاربر --------

@app.post("/register") 
def register(user: User):
    cursor.execute("SELECT * FROM users WHERE username=%s", (user.username,))
    if cursor.fetchone():    raise HTTPException(status_code=400, detail="نام کاربری قبلاً ثبت شده است")
    cursor.execute( "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (user.username, user.password, user.role) ) 
    conn.commit() 
    return {"message": "ثبت‌نام با موفقیت انجام شد"}

#-------- ورود کاربر --------

@app.post("/login") 
def login(user: User): 
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (user.username, user.password)) 
    result = cursor.fetchone() 
    if result:return {"message": "ورود موفق", "user": result}
raise HTTPException(status_code=401, detail="نام کاربری یا رمز عبور اشتباه است")

#-------- تایید استاد --------

@app.post("/approve_teacher/{user_id}") 
def approve_teacher(user_id: int):
    cursor.execute("UPDATE users SET approved=TRUE WHERE id=%s AND role='teacher'",(user_id,)) 
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="استاد یافت نشد") 
    conn.commit() 
    return {"message": "استاد تایید شد"}


