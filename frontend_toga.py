# Frontend-toga.py - سازگار با Python 3.13
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from toga import Dialog
import requests
import json
import os
import sys
from datetime import datetime, timedelta

class QuranApp(toga.App):
    def __init__(self):
        super().__init__("Quran Academy", "com.quranapp.app")
        self.current_user = None
        self.user_token = None
        self.user_role = None
        self.token_expiry = None
        self.BASE_URL = "http://localhost:8000"
        
    def get_auth_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.user_token:
            headers["Authorization"] = f"Bearer {self.user_token}"
        return headers
    
    def is_token_valid(self):
        if not self.user_token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry
    
    def logout(self, widget=None):
        self.current_user = None
        self.user_token = None
        self.user_role = None
        self.token_expiry = None
        self.show_login_screen()
        self.dialog_info("Info", "Logged out successfully")
    
    def make_authenticated_request(self, method, endpoint, **kwargs):
        if not self.is_token_valid():
            self.dialog_info("Session Expired", "Please login again")
            self.logout()
            return None
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = self.get_auth_headers()
        
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers
        
        try:
            response = requests.request(method, url, **kwargs, timeout=30)
            return response
        except requests.exceptions.ConnectionError:
            self.dialog_error("Connection Error", "Cannot connect to server. Please check if the server is running.")
            return None
        except Exception as e:
            self.dialog_error("Error", f"Connection error: {str(e)}")
            return None

    # توابع جدید برای dialog (سازگار با Toga جدید)
    def dialog_info(self, title, message):
        dialog = Dialog(title=title)
        dialog.text(message)
        dialog.show()

    def dialog_error(self, title, message):
        dialog = Dialog(title=title, style=Pack(color="red"))
        dialog.text(message)
        dialog.show()

    def dialog_confirm(self, title, message, on_confirm):
        dialog = Dialog(title=title)
        dialog.text(message)
        dialog.on_result = on_confirm
        dialog.show()
    
    def startup(self):
        self.main_window = toga.MainWindow(
            title="Quran Academy - Islamic Learning Platform",
            size=(500, 800)
        )
        self.show_login_screen()
        self.main_window.show()
    
    def show_login_screen(self, widget=None):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=0, alignment=CENTER))
        
        header_box = toga.Box(style=Pack(direction=ROW, padding=25, background_color="#0D8E3D", alignment=CENTER))
        header_icon = toga.Label(
            "📚",
            style=Pack(font_size=32, padding_right=15, color="white")
        )
        header_text = toga.Label(
            "QURAN ACADEMY",
            style=Pack(color="white", font_size=24, font_weight="bold")
        )
        header_box.add(header_icon)
        header_box.add(header_text)
        main_box.add(header_box)
        
        subtitle_label = toga.Label(
            "Islamic Education Platform",
            style=Pack(text_align=CENTER, font_size=14, color="#0D8E3D", padding=10)
        )
        main_box.add(subtitle_label)
        
        content_box = toga.Box(style=Pack(direction=COLUMN, padding=30, alignment=CENTER))
        
        self.username_input = toga.TextInput(
            placeholder="Username (Teachers) or Email (Students)",
            style=Pack(padding=12, width=320, background_color="#f8f9fa")
        )
        
        self.password_input = toga.PasswordInput(
            placeholder="Password", 
            style=Pack(padding=12, width=320, background_color="#f8f9fa")
        )
        
        login_btn = toga.Button(
            "📖 Login to Account",
            on_press=self.login,
            style=Pack(padding=15, background_color="#0D8E3D", color="white", width=250, font_weight="bold")
        )
        
        separator = toga.Label(
            "―" * 30,
            style=Pack(text_align=CENTER, color="#ccc", padding=10)
        )
        
        register_box = toga.Box(style=Pack(direction=COLUMN, padding=5, alignment=CENTER))
        
        register_label = toga.Label(
            "Create New Account:",
            style=Pack(text_align=CENTER, font_size=12, color="#666", padding=5)
        )
        
        register_student_btn = toga.Button(
            "👨‍🎓 Register as Student",
            on_press=self.show_register_student,
            style=Pack(padding=12, background_color="#2196F3", color="white", width=220)
        )
        
        register_teacher_btn = toga.Button(
            "👨‍🏫 Register as Teacher",
            on_press=self.show_register_teacher,
            style=Pack(padding=12, background_color="#FF9800", color="white", width=220)
        )
        
        help_label = toga.Label(
            "💡 Note: Students login with email, Teachers with username",
            style=Pack(text_align=CENTER, font_size=10, color="#888", padding=15)
        )
        
        content_box.add(self.username_input)
        content_box.add(self.password_input)
        content_box.add(login_btn)
        content_box.add(separator)
        content_box.add(register_label)
        register_box.add(register_student_btn)
        register_box.add(register_teacher_btn)
        content_box.add(register_box)
        content_box.add(help_label)
        
        main_box.add(content_box)
        self.main_window.content = main_box

    # بقیه توابع بدون تغییر می‌مانند...
    # فقط جایگزین کردن main_window.info_dialog و main_window.error_dialog با:
    # self.dialog_info() و self.dialog_error()

    def register_student(self, widget):
        try:
            name = self.name_input.value.strip()
            email = self.email_input.value.strip()
            password = self.password_input.value
            level = self.level_input.value
            
            if not all([name, email, password, level]):
                self.dialog_error("Error", "Please fill all fields")
                return
            
            response = requests.post(
                f"{self.BASE_URL}/register/student",
                json={"name": name, "email": email, "password": password, "level": level},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                self.dialog_info("Success", "Student registration successful! Please login with your email.")
                self.show_login_screen()
            else:
                error_msg = response.json().get("detail", "Registration failed")
                self.dialog_error("Error", f"Registration failed: {error_msg}")
                
        except Exception as e:
            self.dialog_error("Error", f"Connection error: {str(e)}")

    def login(self, widget):
        try:
            identifier = self.username_input.value.strip()
            password = self.password_input.value
            
            if not identifier or not password:
                self.dialog_error("Error", "Please enter both username/email and password")
                return
            
            response = requests.post(
                f"{self.BASE_URL}/api/login",
                json={"username": identifier, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Login response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                self.user_token = result['access_token']
                self.token_expiry = datetime.now() + timedelta(hours=1)
                
                user_response = self.make_authenticated_request("GET", "/users/me")
                
                if user_response and user_response.status_code == 200:
                    user_data = user_response.json()
                    self.current_user = user_data
                    self.user_role = user_data['role']
                    
                    if self.user_role == 'student':
                        self.show_student_dashboard(user_data)
                    elif self.user_role == 'teacher':
                        self.show_teacher_dashboard(user_data)
                    else:
                        self.dialog_info("Success", f"Login successful! Welcome {user_data['full_name']}")
                else:
                    self.dialog_error("Error", "Failed to get user information")
                    
            else:
                error_msg = response.json().get("detail", "Login failed")
                self.dialog_error("Error", f"Login failed: {error_msg}")
                
        except Exception as e:
            self.dialog_error("Error", f"Connection error: {str(e)}")

def main():
    return QuranApp()

if __name__ == "__main__":
    app = main()
    app.main_loop()
