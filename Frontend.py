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
    
    def startup(self):
        # ایجاد صفحه اصلی (معادل ScreenManager در Kivy)
        self.main_box = toga.Box(style=Pack(direction=COLUMN, padding=40, spacing=20))
        
        # ایجاد محتوای صفحه لاگین (معادل LoginScreen)
        self.create_login_screen()
        
        # ایجاد پنجره اصلی
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 600))
        self.main_window.content = self.main_box
        self.main_window.show()
    
    def create_login_screen(self):
        # پاک کردن محتوای قبلی
        self.main_box.children.clear()
        
        # عنوان
        title_label = toga.Label(
            "Quran App Login",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # فیلدهای ورودی
        self.username_input = toga.TextInput(
            placeholder="Username",
            style=Pack(padding=10, width=300)
        )
        
        self.password_input = toga.PasswordInput(
            placeholder="Password",
            style=Pack(padding=10, width=300)
        )
        
        # دکمه‌ها
        login_btn = toga.Button(
            "Login",
            on_press=self.login,
            style=Pack(padding=15, background_color="#4CAF50", color="white")
        )
        
        register_student_btn = toga.Button(
            "Register Student",
            on_press=self.go_to_register_student,
            style=Pack(padding=15, background_color="#2196F3", color="white")
        )
        
        register_teacher_btn = toga.Button(
            "Register Teacher",
            on_press=self.go_to_register_teacher,
            style=Pack(padding=15, background_color="#FF9800", color="white")
        )
        
        # اضافه کردن ویجت‌ها به صفحه
        self.main_box.add(title_label)
        self.main_box.add(self.username_input)
        self.main_box.add(self.password_input)
        self.main_box.add(login_btn)
        self.main_box.add(register_student_btn)
        self.main_box.add(register_teacher_btn)
    
    def create_dashboard_screen(self):
        # پاک کردن محتوای قبلی
        self.main_box.children.clear()
        
        # محتوای دشبورد
        title_label = toga.Label(
            f"Welcome, {self.username}!",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        user_info = toga.Label(
            "You are successfully logged in to Quran App",
            style=Pack(text_align="center", font_size=14, padding_bottom=30)
        )
        
        logout_btn = toga.Button(
            "Logout",
            on_press=self.logout,
            style=Pack(padding=15, background_color="#f44336", color="white")
        )
        
        # اضافه کردن ویجت‌ها
        self.main_box.add(title_label)
        self.main_box.add(user_info)
        self.main_box.add(logout_btn)
    
    def create_register_student_screen(self):
        # پاک کردن محتوای قبلی
        self.main_box.children.clear()
        
        # ایجاد فرم ثبت‌نام دانش‌آموز
        title_label = toga.Label(
            "Student Registration",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        back_btn = toga.Button(
            "← Back to Login",
            on_press=self.go_to_login,
            style=Pack(padding=10, background_color="#666", color="white")
        )
        
        self.main_box.add(back_btn)
        self.main_box.add(title_label)
        
        # اینجا می‌تونید فیلدهای ثبت‌نام دانش‌آموز رو اضافه کنید
    
    def create_register_teacher_screen(self):
        # پاک کردن محتوای قبلی
        self.main_box.children.clear()
        
        # ایجاد فرم ثبت‌نام معلم
        title_label = toga.Label(
            "Teacher Registration",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        back_btn = toga.Button(
            "← Back to Login",
            on_press=self.go_to_login,
            style=Pack(padding=10, background_color="#666", color="white")
        )
        
        self.main_box.add(back_btn)
        self.main_box.add(title_label)
        
        # اینجا می‌تونید فیلدهای ثبت‌نام معلم رو اضافه کنید
    
    async def login(self, widget):
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        
        print(f"🔐 Attempting login with username: {username}")
        
        if not username or not password:
            self.show_dialog("Error", "Please enter username and password")
            return
        
        try:
            payload = {"username": username, "password": password}
            print(f"📤 Sending payload: {payload}")
            
            response = requests.post(f"{BASE_URL}/login", json=payload, verify=False, timeout=10)
            
            print(f"📥 Response status code: {response.status_code}")
            print(f"📥 Response content: {response.text}")
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.token = token
                self.username = username
                print(f"✅ Login successful! Token: {token}")
                self.show_dialog("Success", "Login successful! Going to dashboard...")
                self.create_dashboard_screen()
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                print(f"❌ Login failed: {error_msg}")
                self.show_dialog("Error", f"Login failed: {error_msg}")
                
        except Exception as e:
            print(f"💥 Exception during login: {str(e)}")
            self.show_dialog("Error", f"Connection error: {str(e)}")
    
    def go_to_register_student(self, widget):
        print("🔄 Going to student registration")
        self.create_register_student_screen()
    
    def go_to_register_teacher(self, widget):
        print("🔄 Going to teacher registration")
        self.create_register_teacher_screen()
    
    def go_to_login(self, widget):
        print("🔄 Going back to login")
        self.create_login_screen()
    
    def logout(self, widget):
        print("🚪 Logging out")
        self.token = None
        self.username = None
        self.create_login_screen()
        self.show_dialog("Success", "Logged out successfully!")
    
    def show_dialog(self, title, text):
        # BeeWare از dialog داخلی استفاده می‌کند
        if "Error" in title:
            self.main_window.error_dialog(title, text)
        else:
            self.main_window.info_dialog(title, text)

def main():
    return QuranApp()

if __name__ == "__main__":
    print("🚀 Starting Quran App with BeeWare...")
    app = main()
    app.main_loop()
