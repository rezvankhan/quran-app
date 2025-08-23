# ======================================
# PowerShell Script برای نصب و اجرای سرور
# مسیر اپ: C:\python\quran
# ======================================

# رفتن به مسیر پروژه
cd "C:\python\quran"

# آپدیت pip
Write-Host "Updating pip..."
C:\Users\Amir\AppData\Local\Programs\Python\Python313\python.exe -m pip install --upgrade pip

# نصب کتابخانه‌های لازم
Write-Host "Installing required packages..."
C:\Users\Amir\AppData\Local\Programs\Python\Python313\python.exe -m pip install fastapi uvicorn pymysql passlib[bcrypt] python-jose requests kivy kivymd

# اجرای سرور FastAPI با uvicorn
Write-Host "Starting FastAPI server..."
uvicorn backend:app --reload --host 0.0.0.0 --port 8080
