import mysql.connector

# اتصال به MySQL (قبل از ساخت دیتابیس)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)
cursor = conn.cursor()

# ساخت دیتابیس اگر وجود نداشت
cursor.execute("CREATE DATABASE IF NOT EXISTS quran_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
conn.close()

# اتصال به دیتابیس quran_db
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="quran_db"
)
cursor = conn.cursor()

# ساخت جدول‌ها
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL,
    approved BOOLEAN DEFAULT FALSE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    teacher_id INT NOT NULL,
    class_type VARCHAR(100),
    price_eth FLOAT DEFAULT 0,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    title VARCHAR(200),
    FOREIGN KEY (class_id) REFERENCES classes(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    question_text TEXT,
    choices TEXT,
    correct_answer VARCHAR(200),
    score FLOAT DEFAULT 1.0,
    FOREIGN KEY (exam_id) REFERENCES exams(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    exam_id INT NOT NULL,
    responses TEXT,
    score FLOAT,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (exam_id) REFERENCES exams(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
)
""")

print("✅ دیتابیس و جدول‌ها با موفقیت ساخته شدند.")
conn.close()