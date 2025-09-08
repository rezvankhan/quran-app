# Frontend.py - کامل با مدیریت خطا و timeout
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER
import requests
import json

class QuranApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 700))
        self.show_login_screen()
        self.main_window.show()
    
    def show_login_screen(self, widget=None):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=30, alignment=CENTER))
        
        title_label = toga.Label(
            "📖 Quran App",
            style=Pack(text_align=CENTER, font_size=24, font_weight="bold", padding=20)
        )
        
        # تغییر placeholder برای راهنمایی کاربران
        self.username_input = toga.TextInput(
            placeholder="Username (Teachers) or Email (Students)",
            style=Pack(padding=10, flex=1)
        )
        
        self.password_input = toga.PasswordInput(
            placeholder="Password", 
            style=Pack(padding=10, flex=1)
        )
        
        login_btn = toga.Button(
            "🔐 Login",
            on_press=self.login,
            style=Pack(padding=15, background_color="#4CAF50", color="white")
        )
        
        register_student_btn = toga.Button(
            "🎓 Register Student",
            on_press=self.show_register_student,
            style=Pack(padding=15, background_color="#2196F3", color="white")
        )
        
        register_teacher_btn = toga.Button(
            "👨‍🏫 Register Teacher",
            on_press=self.show_register_teacher,
            style=Pack(padding=15, background_color="#FF9800", color="white")
        )
        
        # اضافه کردن راهنمایی
        help_label = toga.Label(
            "Note: Students login with email, Teachers with username",
            style=Pack(text_align=CENTER, font_size=10, color="gray", padding=10)
        )
        
        main_box.add(title_label)
        main_box.add(self.username_input)
        main_box.add(self.password_input)
        main_box.add(login_btn)
        main_box.add(register_student_btn)
        main_box.add(register_teacher_btn)
        main_box.add(help_label)
        
        self.main_window.content = main_box
    
    def show_register_student(self, widget):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=30, alignment=CENTER))
        
        title_label = toga.Label(
            "🎓 Register Student",
            style=Pack(text_align=CENTER, font_size=20, font_weight="bold", padding=10)
        )
        
        self.name_input = toga.TextInput(placeholder="Full Name", style=Pack(padding=10))
        self.email_input = toga.TextInput(placeholder="Email (will be used for login)", style=Pack(padding=10))
        self.password_input = toga.PasswordInput(placeholder="Password", style=Pack(padding=10))
        self.level_input = toga.Selection(
            items=["Beginner", "Intermediate", "Advanced"],
            style=Pack(padding=10)
        )
        
        register_btn = toga.Button(
            "✅ Register",
            on_press=self.register_student,
            style=Pack(padding=15, background_color="#4CAF50", color="white")
        )
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_login_screen,
            style=Pack(padding=15, background_color="#f44336", color="white")
        )
        
        main_box.add(title_label)
        main_box.add(self.name_input)
        main_box.add(self.email_input)
        main_box.add(self.password_input)
        main_box.add(self.level_input)
        main_box.add(register_btn)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def show_register_teacher(self, widget):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=30, alignment=CENTER))
        
        title_label = toga.Label(
            "👨‍🏫 Register Teacher",
            style=Pack(text_align=CENTER, font_size=20, font_weight="bold", padding=10)
        )
        
        self.teacher_username = toga.TextInput(placeholder="Username (for login)", style=Pack(padding=10))
        self.teacher_password = toga.PasswordInput(placeholder="Password", style=Pack(padding=10))
        self.teacher_name = toga.TextInput(placeholder="Full Name", style=Pack(padding=10))
        self.teacher_email = toga.TextInput(placeholder="Email", style=Pack(padding=10))
        self.teacher_specialty = toga.TextInput(placeholder="Specialty", style=Pack(padding=10))
        
        register_btn = toga.Button(
            "✅ Register",
            on_press=self.register_teacher,
            style=Pack(padding=15, background_color="#4CAF50", color="white")
        )
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_login_screen,
            style=Pack(padding=15, background_color="#f44336", color="white")
        )
        
        main_box.add(title_label)
        main_box.add(self.teacher_username)
        main_box.add(self.teacher_password)
        main_box.add(self.teacher_name)
        main_box.add(self.teacher_email)
        main_box.add(self.teacher_specialty)
        main_box.add(register_btn)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def login(self, widget):
        try:
            identifier = self.username_input.value.strip()
            password = self.password_input.value
            
            if not identifier or not password:
                self.main_window.error_dialog("Error", "Please enter both username/email and password")
                return
            
            # استفاده از endpoint صحیح لاگین
            response = requests.post(
                "https://quran-app-kw38.onrender.com/login",  # endpoint صحیح
                json={
                    "username": identifier,  # برای Students: email, برای Teachers: username
                    "password": password
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            # چاپ پاسخ برای دیباگ
            print(f"Login Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                user_data = response.json()
                self.main_window.info_dialog("Success", f"Login successful!\nWelcome {user_data['user']['full_name']}")
                # اینجا می‌توانید به صفحه اصلی بروید
                
            elif response.status_code == 401:
                self.main_window.error_dialog("Error", "Invalid credentials! Please check your username/email and password")
                
            else:
                error_msg = response.json().get("detail", "Login failed! Please try again.")
                self.main_window.error_dialog("Error", f"Login failed: {error_msg}")
                
        except requests.exceptions.Timeout:
            self.main_window.error_dialog("Error", "Connection timeout! Please try again.")
        except requests.exceptions.ConnectionError:
            self.main_window.error_dialog("Error", "Cannot connect to server. Check your internet connection.")
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")
    
    def register_student(self, widget):
        try:
            name = self.name_input.value.strip()
            email = self.email_input.value.strip()
            password = self.password_input.value
            level = self.level_input.value
            
            if not all([name, email, password, level]):
                self.main_window.error_dialog("Error", "Please fill all fields")
                return
            
            response = requests.post(
                "https://quran-app-kw38.onrender.com/register/student",
                json={
                    "name": name,
                    "email": email,
                    "password": password,
                    "level": level
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.main_window.info_dialog("Success", f"Student registration successful!\nUser ID: {result['user_id']}\nPlease login with your email: {email}")
                self.show_login_screen()
            else:
                error_msg = response.json().get("detail", "Registration failed")
                self.main_window.error_dialog("Error", f"Registration failed: {error_msg}")
                
        except requests.exceptions.Timeout:
            self.main_window.error_dialog("Error", "Connection timeout! Please try again.")
        except requests.exceptions.ConnectionError:
            self.main_window.error_dialog("Error", "Cannot connect to server. Check your internet connection.")
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")
    
    def register_teacher(self, widget):
        try:
            username = self.teacher_username.value.strip()
            password = self.teacher_password.value
            full_name = self.teacher_name.value.strip()
            email = self.teacher_email.value.strip()
            specialty = self.teacher_specialty.value.strip()
            
            if not all([username, password, full_name, email, specialty]):
                self.main_window.error_dialog("Error", "Please fill all fields")
                return
            
            response = requests.post(
                "https://quran-app-kw38.onrender.com/register/teacher",
                json={
                    "username": username,
                    "password": password,
                    "full_name": full_name,
                    "email": email,
                    "specialty": specialty
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.main_window.info_dialog("Success", f"Teacher registration successful!\nUser ID: {result['user_id']}\nPlease login with your username: {username}")
                self.show_login_screen()
            else:
                error_msg = response.json().get("detail", "Registration failed")
                self.main_window.error_dialog("Error", f"Registration failed: {error_msg}")
                
        except requests.exceptions.Timeout:
            self.main_window.error_dialog("Error", "Connection timeout! Please try again.")
        except requests.exceptions.ConnectionError:
            self.main_window.error_dialog("Error", "Cannot connect to server. Check your internet connection.")
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")

def main():
    return QuranApp("Quran App", "com.quranapp.app")

if __name__ == "__main__":
    app = main()
    app.main_loop()
