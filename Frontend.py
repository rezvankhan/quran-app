import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import requests
import ssl
import urllib3
import json
import asyncio
import warnings

# غیرفعال کردن هشدارها
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore", category=DeprecationWarning)

# URL پایه API - با قابلیت تشخیص خودکار
class APIClient:
    def __init__(self):
        self.base_urls = [
            "https://quran-global-api.onrender.com",
            "https://quran-app-kw38.onrender.com",
            "http://localhost:8000"  # برای توسعه محلی
        ]
        self.current_base_url = None
        self.detect_base_url()
    
    def detect_base_url(self):
        """تشخیص خودکار آدرس سرور"""
        for url in self.base_urls:
            try:
                print(f"🔍 Testing API URL: {url}")
                response = requests.get(f"{url}/", timeout=5, verify=False)
                if response.status_code == 200:
                    self.current_base_url = url
                    print(f"✅ Found active API: {url}")
                    return
            except:
                continue
        
        print("❌ No active API server found!")
        self.current_base_url = self.base_urls[0]  # fallback به اولین آدرس
    
    def get_base_url(self):
        return self.current_base_url

# ایجاد کلient API
api_client = APIClient()
BASE_URL = api_client.get_base_url()

class QuranApp(toga.App):
    def __init__(self):
        super().__init__('Quran App', 'com.quran.app')
        self.token = None
        self.username = None
        self.current_screen = "login"
    
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 600))
        self.show_login_screen()
        self.main_window.show()
    
    def show_login_screen(self):
        self.current_screen = "login"
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=40))
        
        title_label = toga.Label(
            "Quran App Login",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # اضافه کردن نمایش آدرس API
        api_label = toga.Label(
            f"API: {BASE_URL}",
            style=Pack(text_align="center", font_size=10, color="gray", padding_bottom=10)
        )
        
        self.username_input = toga.TextInput(
            placeholder="Username",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.password_input = toga.PasswordInput(
            placeholder="Password",
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
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
        
        main_box.add(title_label)
        main_box.add(api_label)  # اضافه کردن نمایش آدرس API
        main_box.add(self.username_input)
        main_box.add(self.password_input)
        main_box.add(login_btn)
        main_box.add(register_student_btn)
        main_box.add(register_teacher_btn)
        
        self.main_window.content = main_box
    
    # بقیه متدها بدون تغییر...
    
    async def register_student(self):
        username = self.student_username.value.strip()
        password = self.student_password.value.strip()
        email = self.student_email.value.strip()
        fullname = self.student_fullname.value.strip()
        
        if not all([username, password, fullname]):
            self.show_error("Error", "Please fill all required fields (username, password, full name)")
            return
        
        try:
            payload = {
                "username": username,
                "password": password,
                "full_name": fullname,
                "email": email,
                "grade": "General"
            }
            
            print(f"📤 Registering student: {payload}")
            print(f"📤 Sending to: {BASE_URL}/register-student")
            
            # تست سلامت سرور قبل از ارسال
            try:
                health_check = requests.get(f"{BASE_URL}/", timeout=5, verify=False)
                print(f"🏥 Server health: {health_check.status_code}")
            except Exception as e:
                print(f"❌ Server health check failed: {e}")
                self.show_error("Error", f"Cannot connect to server: {e}")
                return
            
            response = requests.post(f"{BASE_URL}/register-student", json=payload, verify=False, timeout=30)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    message = response_data.get('message', 'Registration successful')
                    self.show_info("Success", message)
                    self.show_login_screen()
                except json.JSONDecodeError:
                    self.show_info("Success", "Registration successful!")
                    self.show_login_screen()
            else:
                error_msg = self.parse_error(response)
                self.show_error("Error", f"Registration failed: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            self.show_error("Error", "Cannot connect to server. Please check the API URL.")
        except requests.exceptions.Timeout:
            self.show_error("Error", "Server timeout")
        except Exception as e:
            print(f"💥 Exception during registration: {str(e)}")
            self.show_error("Error", f"Registration error: {str(e)}")
    
    def parse_error(self, response):
        """پارس کردن خطا از response"""
        try:
            if response.text.strip():
                error_data = response.json()
                return error_data.get('detail', response.text)
            else:
                return f"Server returned {response.status_code}"
        except:
            return response.text if response.text else f"Server returned {response.status_code}"
    
    # بقیه متدها بدون تغییر...

def main():
    return QuranApp()

if __name__ == "__main__":
    print("🚀 Starting Quran App...")
    print(f"🌐 Using API: {BASE_URL}")
    app = main()
    app.main_loop()
