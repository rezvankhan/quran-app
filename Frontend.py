import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import requests
import ssl
import urllib3
import json
import asyncio

# غیرفعال کردن هشدارهای SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# URL پایه API
BASE_URL = "https://quran-app-kw38.onrender.com"

class QuranApp(toga.App):
    def __init__(self):
        super().__init__('Quran App', 'com.quran.app')
        self.token = None
        self.username = None
        self.current_screen = "login"
    
    def startup(self):
        # ایجاد پنجره اصلی
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 600))
        self.show_login_screen()
        self.main_window.show()
    
    def show_login_screen(self):
        self.current_screen = "login"
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=40))
        
        # عنوان
        title_label = toga.Label(
            "Quran App Login",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # فیلدهای ورودی
        self.username_input = toga.TextInput(
            placeholder="Username",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.password_input = toga.PasswordInput(
            placeholder="Password",
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        # دکمه‌ها
        login_btn = toga.Button(
            "Login",
            on_press=self.login_handler,
            style=Pack(padding=15, background_color="#4CAF50", color="white", padding_bottom=10)
        )
        
        register_student_btn = toga.Button(
            "Register Student",
            on_press=self.go_to_register_student,
            style=Pack(padding=15, background_color="#2196F3", color="white", padding_bottom=10)
        )
        
        register_teacher_btn = toga.Button(
            "Register Teacher",
            on_press=self.go_to_register_teacher,
            style=Pack(padding=15, background_color="#FF9800", color="white")
        )
        
        # اضافه کردن ویجت‌ها
        main_box.add(title_label)
        main_box.add(self.username_input)
        main_box.add(self.password_input)
        main_box.add(login_btn)
        main_box.add(register_student_btn)
        main_box.add(register_teacher_btn)
        
        self.main_window.content = main_box
    
    def show_dashboard_screen(self):
        self.current_screen = "dashboard"
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=40))
        
        title_label = toga.Label(
            f"Welcome, {self.username}!",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        user_info = toga.Label(
            "You are successfully logged in",
            style=Pack(text_align="center", font_size=14, padding_bottom=30)
        )
        
        logout_btn = toga.Button(
            "Logout",
            on_press=self.logout,
            style=Pack(padding=15, background_color="#f44336", color="white")
        )
        
        main_box.add(title_label)
        main_box.add(user_info)
        main_box.add(logout_btn)
        
        self.main_window.content = main_box
    
    def show_register_student_screen(self):
        self.current_screen = "register_student"
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        title_label = toga.Label(
            "Register Student",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # فیلدهای ثبت‌نام دانش‌آموز
        self.student_username = toga.TextInput(
            placeholder="Student Username",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.student_password = toga.PasswordInput(
            placeholder="Student Password",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.student_email = toga.TextInput(
            placeholder="Email",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.student_fullname = toga.TextInput(
            placeholder="Full Name",
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        register_btn = toga.Button(
            "Register",
            on_press=self.register_student_handler,
            style=Pack(padding=15, background_color="#4CAF50", color="white", padding_bottom=10)
        )
        
        back_btn = toga.Button(
            "Back to Login",
            on_press=self.show_login_screen,
            style=Pack(padding=15, background_color="#9E9E9E", color="white")
        )
        
        main_box.add(title_label)
        main_box.add(self.student_username)
        main_box.add(self.student_password)
        main_box.add(self.student_email)
        main_box.add(self.student_fullname)
        main_box.add(register_btn)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def show_register_teacher_screen(self):
        self.current_screen = "register_teacher"
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        title_label = toga.Label(
            "Register Teacher",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # فیلدهای ثبت‌نام معلم
        self.teacher_username = toga.TextInput(
            placeholder="Teacher Username",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.teacher_password = toga.PasswordInput(
            placeholder="Teacher Password",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.teacher_email = toga.TextInput(
            placeholder="Email",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.teacher_fullname = toga.TextInput(
            placeholder="Full Name",
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        register_btn = toga.Button(
            "Register",
            on_press=self.register_teacher_handler,
            style=Pack(padding=15, background_color="#4CAF50", color="white", padding_bottom=10)
        )
        
        back_btn = toga.Button(
            "Back to Login",
            on_press=self.show_login_screen,
            style=Pack(padding=15, background_color="#9E9E9E", color="white")
        )
        
        main_box.add(title_label)
        main_box.add(self.teacher_username)
        main_box.add(self.teacher_password)
        main_box.add(self.teacher_email)
        main_box.add(self.teacher_fullname)
        main_box.add(register_btn)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def login_handler(self, widget):
        # استفاده از asyncio برای اجرای تابع async
        asyncio.create_task(self.login())
    
    def register_student_handler(self, widget):
        asyncio.create_task(self.register_student())
    
    def register_teacher_handler(self, widget):
        asyncio.create_task(self.register_teacher())
    
    async def login(self):
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        
        print(f"🔐 Attempting login with username: {username}")
        
        if not username or not password:
            self.show_error("Error", "Please enter username and password")
            return
        
        try:
            payload = {"username": username, "password": password}
            print(f"📤 Sending payload: {payload}")
            
            response = requests.post(f"{BASE_URL}/login", json=payload, verify=False, timeout=30)
            
            print(f"📥 Response status code: {response.status_code}")
            print(f"📥 Response content: {response.text}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    token = response_data.get("access_token")
                    if token:
                        self.token = token
                        self.username = username
                        print(f"✅ Login successful! Token: {token}")
                        self.show_info("Success", "Login successful!")
                        self.show_dashboard_screen()
                    else:
                        self.show_error("Error", "No access token received")
                except json.JSONDecodeError:
                    self.show_error("Error", "Invalid JSON response from server")
            else:
                try:
                    error_msg = response.json().get('detail', 'Unknown error')
                    print(f"❌ Login failed: {error_msg}")
                    self.show_error("Error", f"Login failed: {error_msg}")
                except json.JSONDecodeError:
                    self.show_error("Error", f"Server error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            self.show_error("Error", "Connection error: Cannot connect to server")
        except requests.exceptions.Timeout:
            self.show_error("Error", "Connection timeout: Server took too long to respond")
        except Exception as e:
            print(f"💥 Exception during login: {str(e)}")
            self.show_error("Error", f"Unexpected error: {str(e)}")
    
    async def register_student(self):
        username = self.student_username.value.strip()
        password = self.student_password.value.strip()
        email = self.student_email.value.strip()
        fullname = self.student_fullname.value.strip()
        
        if not all([username, password, email, fullname]):
            self.show_error("Error", "Please fill all fields")
            return
        
        try:
            payload = {
                "username": username,
                "password": password,
                "email": email,
                "full_name": fullname,
                "role": "student"
            }
            
            print(f"📤 Registering student: {payload}")
            response = requests.post(f"{BASE_URL}/register", json=payload, verify=False, timeout=30)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
            if response.status_code == 200:
                self.show_info("Success", "Student registered successfully!")
                self.show_login_screen()
            else:
                # بررسی اگر پاسخ JSON نیست
                if response.text.strip():
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('detail', 'Registration failed')
                    except json.JSONDecodeError:
                        error_msg = response.text
                else:
                    error_msg = "Registration failed - Empty response from server"
                
                self.show_error("Error", f"Registration failed: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            self.show_error("Error", "Cannot connect to server")
        except requests.exceptions.Timeout:
            self.show_error("Error", "Server timeout")
        except Exception as e:
            self.show_error("Error", f"Registration error: {str(e)}")
    
    async def register_teacher(self):
        username = self.teacher_username.value.strip()
        password = self.teacher_password.value.strip()
        email = self.teacher_email.value.strip()
        fullname = self.teacher_fullname.value.strip()
        
        if not all([username, password, email, fullname]):
            self.show_error("Error", "Please fill all fields")
            return
        
        try:
            payload = {
                "username": username,
                "password": password,
                "email": email,
                "full_name": fullname,
                "role": "teacher"
            }
            
            print(f"📤 Registering teacher: {payload}")
            response = requests.post(f"{BASE_URL}/register", json=payload, verify=False, timeout=30)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
            if response.status_code == 200:
                self.show_info("Success", "Teacher registered successfully!")
                self.show_login_screen()
            else:
                # بررسی اگر پاسخ JSON نیست
                if response.text.strip():
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('detail', 'Registration failed')
                    except json.JSONDecodeError:
                        error_msg = response.text
                else:
                    error_msg = "Registration failed - Empty response from server"
                
                self.show_error("Error", f"Registration failed: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            self.show_error("Error", "Cannot connect to server")
        except requests.exceptions.Timeout:
            self.show_error("Error", "Server timeout")
        except Exception as e:
            self.show_error("Error", f"Registration error: {str(e)}")
    
    def go_to_register_student(self, widget):
        print("🔄 Going to student registration")
        self.show_register_student_screen()
    
    def go_to_register_teacher(self, widget):
        print("🔄 Going to teacher registration")
        self.show_register_teacher_screen()
    
    def logout(self, widget):
        print("🚪 Logging out")
        self.token = None
        self.username = None
        self.show_login_screen()
        self.show_info("Success", "Logged out successfully!")
    
    def show_error(self, title, message):
        """نمایش پیغام خطا"""
        async def show_dialog():
            await self.main_window.error_dialog(title, message)
        asyncio.create_task(show_dialog())
    
    def show_info(self, title, message):
        """نمایش پیغام اطلاعات"""
        async def show_dialog():
            await self.main_window.info_dialog(title, message)
        asyncio.create_task(show_dialog())

def main():
    return QuranApp()

if __name__ == "__main__":
    print("🚀 Starting Quran App with BeeWare...")
    app = main()
    app.main_loop()
