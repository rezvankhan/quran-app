import sqlite3
import os

def check_database():
    try:
        # تغییر این خط به نام صحیح فایل دیتابیس
        conn = sqlite3.connect('quran_db.sqlite3')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("✅ Tables in database:", tables)
        
        # بررسی ساختار جدول students
        if any('students' in table for table in tables):
            cursor.execute("PRAGMA table_info(students)")
            columns = cursor.fetchall()
            print("📋 Students table columns:", columns)
            
            # بررسی داده‌های موجود
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            print("👥 Students data:", students)
        
        conn.close()
        
    except Exception as e:
        print("❌ Error:", e)

check_database()