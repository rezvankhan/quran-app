import requests
import json
import ssl
import urllib3
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock

# غیرفعال کردن هشدارهای SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# URL پایه API
BASE_URL = "https://quran-app-kw38.onrender.com"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        self.username = MDTextField(hint_text="Username", size_hint=(1, None), height=50)
        self.password = MDTextField(hint_text="Password", password=True, size_hint=(1, None), height=50)
        
        login_btn = MDRaisedButton(text="Login", size_hint=(1, None), height=50)
        login_btn.bind(on_press=self.login)
        
        register_student_btn = MDRaisedButton(text="Register Student", size_hint=(1, None), height=50)
        register_student_btn.bind(on_press=self.go_to_register_student)
        
        register_teacher_btn = MDRaisedButton(text="Register Teacher", size_hint=(1, None), height=50)
        register_teacher_btn.bind(on_press=self.go_to_register_teacher)
        
        layout.add_widget(MDLabel(text="Quran App Login", halign="center", font_style="H4"))
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(login_btn)
        layout.add_widget(register_student_btn)
        layout.add_widget(register_teacher_btn)
        
        self.add_widget(layout)
    
    def login(self, instance):
        username = self.username.text
        password = self.password.text
        
        print(f"🔐 Attempting login with username: {username}")
        
        if not username or not password:
            self.show_dialog("Error", "Please enter username and password")
            return
        
        try:
            payload = {"username": username, "password": password}
            print(f"📤 Sending payload: {payload}")
            print(f"🌐 API URL: {BASE_URL}/login")
            
            response = requests.post(f"{BASE_URL}/login", json=payload, verify=False, timeout=10)
            
            print(f"📥 Response status code: {response.status_code}")
            print(f"📥 Response content: {response.text}")
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.manager.token = token
                self.manager.username = username
                print(f"✅ Login successful! Token: {token}")
                self.show_dialog("Success", "Login successful! Going to dashboard...")
                Clock.schedule_once(lambda dt: self.go_to_dashboard(), 1.0)
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                print(f"❌ Login failed: {error_msg}")
                self.show_dialog("Error", f"Login failed: {error_msg}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timeout - Server is not responding")
            self.show_dialog("Error", "Server is not responding. Please try again later.")
        except Exception as e:
            print(f"💥 Exception during login: {str(e)}")
            self.show_dialog("Error", f"Connection error: {str(e)}")
    
    def go_to_dashboard(self):
        print("🔄 Switching to dashboard screen")
        self.manager.current = "dashboard"
    
    def go_to_register_student(self, instance):
        self.manager.current = "register_student"
    
    def go_to_register_teacher(self, instance):
        self.manager.current = "register_teacher"
    
    def show_dialog(self, title, text):
        dialog = MDDialog(title=title, text=text, size_hint=(0.8, 0.4))
        dialog.open()

class RegisterStudentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        self.username = MDTextField(hint_text="Username", size_hint=(1, None), height=50)
        self.password = MDTextField(hint_text="Password", password=True, size_hint=(1, None), height=50)
        self.full_name = MDTextField(hint_text="Full Name", size_hint=(1, None), height=50)
        self.grade = MDTextField(hint_text="Grade", size_hint=(1, None), height=50)
        
        register_btn = MDRaisedButton(text="Register Student", size_hint=(1, None), height=50)
        register_btn.bind(on_press=self.register)
        
        back_btn = MDRaisedButton(text="Back to Login", size_hint=(1, None), height=50)
        back_btn.bind(on_press=self.go_to_login)
        
        layout.add_widget(MDLabel(text="Student Registration", halign="center", font_style="H4"))
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(self.full_name)
        layout.add_widget(self.grade)
        layout.add_widget(register_btn)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def register(self, instance):
        username = self.username.text
        password = self.password.text
        full_name = self.full_name.text
        grade = self.grade.text
        
        print(f"👤 Attempting student registration: {username}")
        
        if not all([username, password, full_name, grade]):
            self.show_dialog("Error", "Please fill all fields")
            return
        
        try:
            payload = {
                "username": username,
                "password": password,
                "full_name": full_name,
                "grade": grade
            }
            print(f"📤 Sending student registration: {payload}")
            
            response = requests.post(f"{BASE_URL}/register-student", json=payload, verify=False, timeout=10)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response content: {response.text}")
            
            if response.status_code == 200:
                self.show_dialog("Success", "Student registration successful!")
                Clock.schedule_once(lambda dt: self.go_to_login(instance), 1.0)
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                print(f"❌ Registration failed: {error_msg}")
                self.show_dialog("Error", f"Registration failed: {error_msg}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timeout - Server is not responding")
            self.show_dialog("Error", "Server is not responding. Please try again later.")
        except Exception as e:
            print(f"💥 Exception during registration: {str(e)}")
            self.show_dialog("Error", f"Connection error: {str(e)}")
    
    def go_to_login(self, instance):
        self.manager.current = "login"
    
    def show_dialog(self, title, text):
        dialog = MDDialog(title=title, text=text, size_hint=(0.8, 0.4))
        dialog.open()

# بقیه کد بدون تغییر...
