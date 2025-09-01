import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import requests
import ssl
import urllib3

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
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 500))
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
            style=Pack(padding=10, width=300, padding_bottom=10)
        )
        
        self.password_input = toga.PasswordInput(
            placeholder="Password",
            style=Pack(padding=10, width=300, padding_bottom=20)
        )
        
        # دکمه‌ها
        login_btn = toga.Button(
            "Login",
            on_press=self.login,
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
        # پیاده‌سازی صفحه ثبت‌نام دانش‌آموز
        self.show_message("Info", "Student registration screen will be implemented")
        self.show_login_screen()
    
    def show_register_teacher_screen(self):
        self.current_screen = "register_teacher"
        # پیاده‌سازی صفحه ثبت‌نام معلم
        self.show_message("Info", "Teacher registration screen will be implemented")
        self.show_login_screen()
    
    async def login(self, widget):
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        
        print(f"🔐 Attempting login with username: {username}")
        
        if not username or not password:
            self.show_message("Error", "Please enter username and password")
            return
        
        try:
            payload = {"username": username, "password": password}
            print(f"📤 Sending payload: {payload}")
            
            response = requests.post(f"{BASE_URL}/login", json=payload, verify=False, timeout=30)
            
            print(f"📥 Response status code: {response.status_code}")
            print(f"📥 Response content: {response.text}")
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.token = token
                self.username = username
                print(f"✅ Login successful! Token: {token}")
                self.show_message("Success", "Login successful! Going to dashboard...")
                self.show_dashboard_screen()
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                print(f"❌ Login failed: {error_msg}")
                self.show_message("Error", f"Login failed: {error_msg}")
                
        except Exception as e:
            print(f"💥 Exception during login: {str(e)}")
            self.show_message("Error", f"Connection error: {str(e)}")
    
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
        self.show_message("Success", "Logged out successfully!")
    
    def show_message(self, title, message):
        if title.lower() == "error":
            self.main_window.error_dialog(title, message)
        else:
            self.main_window.info_dialog(title, message)

def main():
    return QuranApp()

if __name__ == "__main__":
    print("🚀 Starting Quran App with BeeWare...")
    app = main()
    app.main_loop()
