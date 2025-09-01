import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import requests
import ssl
import urllib3

# غیرفعال کردن هشدارهای SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://quran-app-kw38.onrender.com"

class QuranApp(toga.App):
    def __init__(self):
        super().__init__('Quran App', 'com.quran.app')
        self.token = None
        self.username = None
    
    def startup(self):
        # ایجاد صفحه اصلی
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=40))
        
        # ایجاد محتوای صفحه لاگین
        self.create_login_screen(main_box)
        
        # ایجاد پنجره اصلی
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 500))
        self.main_window.content = main_box
        self.main_window.show()
    
    def create_login_screen(self, container):
        # پاک کردن محتوای قبلی
        container.children.clear()
        
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
            on_press=self.register_student,
            style=Pack(padding=15, background_color="#2196F3", color="white", padding_bottom=10)
        )
        
        register_teacher_btn = toga.Button(
            "Register Teacher",
            on_press=self.register_teacher,
            style=Pack(padding=15, background_color="#FF9800", color="white")
        )
        
        # اضافه کردن ویجت‌ها به صفحه
        container.add(title_label)
        container.add(self.username_input)
        container.add(self.password_input)
        container.add(login_btn)
        container.add(register_student_btn)
        container.add(register_teacher_btn)
    
    async def login(self, widget):
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        
        if not username or not password:
            self.main_window.error_dialog("Error", "Please enter username and password")
            return
        
        try:
            payload = {"username": username, "password": password}
            print(f"📤 Sending login request: {payload}")
            
            response = requests.post(f"{BASE_URL}/login", json=payload, verify=False, timeout=10)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response content: {response.text}")
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.token = token
                self.username = username
                print(f"✅ Login successful! Token: {token}")
                self.main_window.info_dialog("Success", "Login successful!")
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                print(f"❌ Login failed: {error_msg}")
                self.main_window.error_dialog("Error", f"Login failed: {error_msg}")
                
        except Exception as e:
            print(f"💥 Exception during login: {str(e)}")
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")
    
    async def register_student(self, widget):
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        
        if not username or not password:
            self.main_window.error_dialog("Error", "Please enter username and password")
            return
        
        try:
            payload = {
                "username": username,
                "password": password,
                "full_name": f"Student {username}",
                "grade": "10"
            }
            print(f"📤 Sending student registration: {payload}")
            
            response = requests.post(f"{BASE_URL}/register-student", json=payload, verify=False, timeout=10)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response content: {response.text}")
            
            if response.status_code == 200:
                self.main_window.info_dialog("Success", "Student registration successful!")
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                self.main_window.error_dialog("Error", f"Registration failed: {error_msg}")
                
        except Exception as e:
            print(f"💥 Exception during registration: {str(e)}")
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")
    
    async def register_teacher(self, widget):
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        
        if not username or not password:
            self.main_window.error_dialog("Error", "Please enter username and password")
            return
        
        try:
            payload = {
                "username": username,
                "password": password,
                "full_name": f"Teacher {username}",
                "specialty": "Quran"
            }
            print(f"📤 Sending teacher registration: {payload}")
            
            response = requests.post(f"{BASE_URL}/register-teacher", json=payload, verify=False, timeout=10)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response content: {response.text}")
            
            if response.status_code == 200:
                self.main_window.info_dialog("Success", "Teacher registration successful! Waiting for admin approval.")
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                self.main_window.error_dialog("Error", f"Registration failed: {error_msg}")
                
        except Exception as e:
            print(f"💥 Exception during registration: {str(e)}")
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")

def main():
    return QuranApp()

if __name__ == "__main__":
    print("🚀 Starting Quran App with BeeWare...")
    app = main()
    app.main_loop()
