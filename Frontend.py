# Frontend.py - کامل و اصلی
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import requests
import json

class QuranApp(toga.App):
    def startup(self):
        # ایجاد main box
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=CENTER))
        
        # عنوان اصلی
        title_label = toga.Label(
            "📖 Quran Learning App",
            style=Pack(padding=20, font_size=24, font_weight="bold", text_align=CENTER)
        )
        
        # زیرعنوان
        subtitle_label = toga.Label(
            "Learn Quran with expert teachers",
            style=Pack(padding=10, font_size=16, text_align=CENTER)
        )
        
        # دکمه‌های اصلی
        button_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        register_student_btn = toga.Button(
            "👨‍🎓 Register as Student",
            on_press=self.go_to_register_student,
            style=Pack(padding=10, background_color="#4CAF50", color="white", font_size=16)
        )
        
        register_teacher_btn = toga.Button(
            "👨‍🏫 Register as Teacher", 
            on_press=self.go_to_register_teacher,
            style=Pack(padding=10, background_color="#2196F3", color="white", font_size=16)
        )
        
        login_btn = toga.Button(
            "🔐 Login",
            on_press=self.go_to_login,
            style=Pack(padding=10, background_color="#FF9800", color="white", font_size=16)
        )
        
        button_box.add(register_student_btn)
        button_box.add(register_teacher_btn)
        button_box.add(login_btn)
        
        # اضافه کردن به main box
        main_box.add(title_label)
        main_box.add(subtitle_label)
        main_box.add(button_box)
        
        # ایجاد window اصلی
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 500))
        self.main_window.content = main_box
        self.main_window.show()

    def go_to_register_student(self, widget):
        self.show_register_student_screen()

    def go_to_register_teacher(self, widget):
        self.show_register_teacher_screen()

    def go_to_login(self, widget):
        self.show_login_screen()

    def show_register_student_screen(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        title = toga.Label("Student Registration", style=Pack(font_size=20, font_weight="bold", padding=10))
        
        self.name_input = toga.TextInput(placeholder="Full Name", style=Pack(padding=5))
        self.email_input = toga.TextInput(placeholder="Email", style=Pack(padding=5))
        self.password_input = toga.PasswordInput(placeholder="Password", style=Pack(padding=5))
        self.level_input = toga.Selection(
            items=["Beginner", "Intermediate", "Advanced"],
            style=Pack(padding=5)
        )
        
        register_btn = toga.Button(
            "Register",
            on_press=self.register_student,
            style=Pack(padding=10, background_color="#4CAF50", color="white")
        )
        
        back_btn = toga.Button(
            "Back",
            on_press=self.show_main_screen,
            style=Pack(padding=10)
        )
        
        box.add(title)
        box.add(self.name_input)
        box.add(self.email_input)
        box.add(self.password_input)
        box.add(self.level_input)
        box.add(register_btn)
        box.add(back_btn)
        
        self.main_window.content = box

    def show_register_teacher_screen(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        title = toga.Label("Teacher Registration", style=Pack(font_size=20, font_weight="bold", padding=10))
        
        self.teacher_username = toga.TextInput(placeholder="Username", style=Pack(padding=5))
        self.teacher_password = toga.PasswordInput(placeholder="Password", style=Pack(padding=5))
        self.teacher_name = toga.TextInput(placeholder="Full Name", style=Pack(padding=5))
        self.teacher_email = toga.TextInput(placeholder="Email", style=Pack(padding=5))
        self.teacher_specialty = toga.TextInput(placeholder="Specialty", style=Pack(padding=5))
        
        register_btn = toga.Button(
            "Register as Teacher",
            on_press=self.register_teacher,
            style=Pack(padding=10, background_color="#2196F3", color="white")
        )
        
        back_btn = toga.Button(
            "Back",
            on_press=self.show_main_screen,
            style=Pack(padding=10)
        )
        
        box.add(title)
        box.add(self.teacher_username)
        box.add(self.teacher_password)
        box.add(self.teacher_name)
        box.add(self.teacher_email)
        box.add(self.teacher_specialty)
        box.add(register_btn)
        box.add(back_btn)
        
        self.main_window.content = box

    def show_login_screen(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        title = toga.Label("Login", style=Pack(font_size=20, font_weight="bold", padding=10))
        
        self.login_username = toga.TextInput(placeholder="Username/Email", style=Pack(padding=5))
        self.login_password = toga.PasswordInput(placeholder="Password", style=Pack(padding=5))
        
        login_btn = toga.Button(
            "Login",
            on_press=self.login_user,
            style=Pack(padding=10, background_color="#FF9800", color="white")
        )
        
        back_btn = toga.Button(
            "Back",
            on_press=self.show_main_screen,
            style=Pack(padding=10)
        )
        
        box.add(title)
        box.add(self.login_username)
        box.add(self.login_password)
        box.add(login_btn)
        box.add(back_btn)
        
        self.main_window.content = box

    def show_main_screen(self, widget=None):
        self.startup()

    def register_student(self, widget):
        try:
            response = requests.post(
                "https://quran-app-kw38.onrender.com/register/student",
                json={
                    "name": self.name_input.value,
                    "email": self.email_input.value,
                    "password": self.password_input.value,
                    "level": self.level_input.value
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                self.main_window.info_dialog("Success", "Student registered successfully!")
                self.show_main_screen()
            else:
                self.main_window.error_dialog("Error", f"Registration failed: {response.text}")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")

    def register_teacher(self, widget):
        try:
            response = requests.post(
                "https://quran-app-kw38.onrender.com/register/teacher",
                json={
                    "username": self.teacher_username.value,
                    "password": self.teacher_password.value,
                    "full_name": self.teacher_name.value,
                    "email": self.teacher_email.value,
                    "specialty": self.teacher_specialty.value
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                self.main_window.info_dialog("Success", "Teacher registered successfully!")
                self.show_main_screen()
            else:
                self.main_window.error_dialog("Error", f"Registration failed: {response.text}")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")

    def login_user(self, widget):
        try:
            response = requests.post(
                "https://quran-app-kw38.onrender.com/login",
                json={
                    "username": self.login_username.value,
                    "password": self.login_password.value
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                self.main_window.info_dialog("Success", 
                    f"Welcome {user_data['user']['full_name']}!\n"
                    f"Role: {user_data['user']['role']}\n"
                    f"Status: {'Approved' if user_data['user']['approved'] else 'Pending Approval'}"
                )
                self.show_main_screen()
            else:
                self.main_window.error_dialog("Error", "Login failed! Check your credentials.")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")

def main():
    return QuranApp("Quran App", "com.quranapp.app")

if __name__ == "__main__":
    print("Starting Quran App...")
    app = main()
    app.main_loop()
