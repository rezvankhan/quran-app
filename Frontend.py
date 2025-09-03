import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import requests
import ssl
import urllib3
import json
import asyncio
import warnings
import time

# غیرفعال کردن هشدارها
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore", category=DeprecationWarning)

# URL پایه API - با قابلیت تشخیص خودکار
class APIClient:
    def __init__(self):
        self.base_urls = [
            "https://quran-app-kw38.onrender.com",
            "http://localhost:8000"
        ]
        self.current_base_url = None
        self.detect_base_url()
    
    def detect_base_url(self):
        """تشخیص خودکار آدرس سرور"""
        print("🔍 Detecting active API server...")
        for url in self.base_urls:
            try:
                print(f"   Testing: {url}")
                response = requests.get(f"{url}/", timeout=10, verify=False)
                if response.status_code == 200:
                    self.current_base_url = url
                    print(f"✅ Found active API: {url}")
                    return
            except Exception as e:
                print(f"   ❌ {url} failed: {e}")
                continue
        
        print("❌ No active API server found! Using fallback")
        self.current_base_url = self.base_urls[0]  # fallback

# ایجاد client API
api_client = APIClient()
BASE_URL = api_client.current_base_url

print(f"🌐 Using API URL: {BASE_URL}")

class QuranApp(toga.App):
    def __init__(self):
        super().__init__('Quran App', 'com.quran.app')
        self.token = None
        self.username = None
        self.current_screen = "login"
    
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 700))
        self.show_login_screen()
        self.main_window.show()
    
    def show_login_screen(self):
        self.current_screen = "login"
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=30))
        
        title_label = toga.Label(
            "📖 Quran App",
            style=Pack(text_align="center", font_size=24, font_weight="bold", padding_bottom=10)
        )
        
        # نمایش آدرس API
        api_status = toga.Label(
            f"API: {BASE_URL}",
            style=Pack(text_align="center", font_size=10, color="gray", padding_bottom=20)
        )
        
        self.username_input = toga.TextInput(
            placeholder="Username",
            style=Pack(padding=12, flex=1, padding_bottom=10)
        )
        
        self.password_input = toga.PasswordInput(
            placeholder="Password",
            style=Pack(padding=12, flex=1, padding_bottom=20)
        )
        
        login_btn = toga.Button(
            "🔐 Login",
            on_press=self.login_handler,
            style=Pack(padding=15, background_color="#4CAF50", color="white", padding_bottom=10)
        )
        
        register_student_btn = toga.Button(
            "🎓 Register Student",
            on_press=self.go_to_register_student,
            style=Pack(padding=15, background_color="#2196F3", color="white", padding_bottom=10)
        )
        
        register_teacher_btn = toga.Button(
            "👨‍🏫 Register Teacher",
            on_press=self.go_to_register_teacher,
            style=Pack(padding=15, background_color="#FF9800", color="white")
        )
        
        # دکمه تست اتصال
        test_connection_btn = toga.Button(
            "📡 Test Connection",
            on_press=self.test_connection,
            style=Pack(padding=10, background_color="#9C27B0", color="white", padding_top=20)
        )
        
        main_box.add(title_label)
        main_box.add(api_status)
        main_box.add(self.username_input)
        main_box.add(self.password_input)
        main_box.add(login_btn)
        main_box.add(register_student_btn)
        main_box.add(register_teacher_btn)
        main_box.add(test_connection_btn)
        
        self.main_window.content = main_box
    
    def test_connection(self, widget):
        """تست اتصال به سرور"""
        async def test():
            try:
                self.show_info("Testing", f"Testing connection to: {BASE_URL}")
                response = requests.get(f"{BASE_URL}/", timeout=10, verify=False)
                if response.status_code == 200:
                    self.show_info("Success", f"✅ Connected to server!\n{response.json()}")
                else:
                    self.show_error("Error", f"Server returned: {response.status_code}")
            except Exception as e:
                self.show_error("Connection Failed", f"Cannot connect to server:\n{str(e)}")
        
        asyncio.create_task(test())
    
    def show_dashboard_screen(self):
        self.current_screen = "dashboard"
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=40))
        
        title_label = toga.Label(
            f"🎉 Welcome, {self.username}!",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        user_info = toga.Label(
            "You are successfully logged in",
            style=Pack(text_align="center", font_size=14, padding_bottom=30)
        )
        
        logout_btn = toga.Button(
            "🚪 Logout",
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
            "🎓 Register Student",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        self.student_username = toga.TextInput(
            placeholder="Username *",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.student_password = toga.PasswordInput(
            placeholder="Password *",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.student_email = toga.TextInput(
            placeholder="Email",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.student_fullname = toga.TextInput(
            placeholder="Full Name *",
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        register_btn = toga.Button(
            "✅ Register",
            on_press=self.register_student_handler,
            style=Pack(padding=15, background_color="#4CAF50", color="white", padding_bottom=10)
        )
        
        back_btn = toga.Button(
            "↩️ Back to Login",
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
            "👨‍🏫 Register Teacher",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        self.teacher_username = toga.TextInput(
            placeholder="Username *",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.teacher_password = toga.PasswordInput(
            placeholder="Password *",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.teacher_email = toga.TextInput(
            placeholder="Email",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.teacher_fullname = toga.TextInput(
            placeholder="Full Name *",
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        register_btn = toga.Button(
            "✅ Register",
            on_press=self.register_teacher_handler,
            style=Pack(padding=15, background_color="#4CAF50", color="white", padding_bottom=10)
        )
        
        back_btn = toga.Button(
            "↩️ Back to Login",
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
            # تست اتصال به سرور
            try:
                test_response = requests.get(f"{BASE_URL}/", verify=False, timeout=10)
                print(f"✅ Connection test: {test_response.status_code}")
            except Exception as e:
                print(f"⚠️  Connection test failed: {e}")
                self.show_error("Error", f"Cannot connect to server: {e}")
                return
            
            payload = {"username": username, "password": password}
            print(f"📤 Sending login request to: {BASE_URL}/login")
            
            response = requests.post(f"{BASE_URL}/login", json=payload, verify=False, timeout=30)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
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
                    self.show_error("Error", "Invalid server response")
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', 'Unknown error')
                    self.show_error("Error", f"Login failed: {error_msg}")
                except json.JSONDecodeError:
                    self.show_error("Error", f"Server returned {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.show_error("Error", "Cannot connect to server. Please check your internet connection.")
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
            elif response.status_code == 404:
                self.show_error("Error", "Endpoint not found. The server may not have the register-student endpoint.")
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
    
    async def register_teacher(self):
        username = self.teacher_username.value.strip()
        password = self.teacher_password.value.strip()
        email = self.teacher_email.value.strip()
        fullname = self.teacher_fullname.value.strip()
        
        if not all([username, password, fullname]):
            self.show_error("Error", "Please fill all required fields (username, password, full name)")
            return
        
        try:
            payload = {
                "username": username,
                "password": password,
                "full_name": fullname,
                "email": email,
                "specialty": "Quran Teaching"
            }
            
            print(f"📤 Registering teacher: {payload}")
            print(f"📤 Sending to: {BASE_URL}/register-teacher")
            
            response = requests.post(f"{BASE_URL}/register-teacher", json=payload, verify=False, timeout=30)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                message = response_data.get('message', 'Registration successful')
                self.show_info("Success", message)
                self.show_login_screen()
            elif response.status_code == 404:
                self.show_error("Error", "Endpoint not found. The server may not have the register-teacher endpoint.")
            else:
                error_msg = self.parse_error(response)
                self.show_error("Error", f"Registration failed: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            self.show_error("Error", "Cannot connect to server")
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
    print("🚀 Starting Quran App...")
    print(f"🌐 Using API: {BASE_URL}")
    app = main()
    app.main_loop()
