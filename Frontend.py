# Frontend.py - نسخه ساده‌شده و اصلاح شده
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import requests
import json

class QuranApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 600))
        self.show_login_screen()
        self.main_window.show()
    
    def show_login_screen(self):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=30, alignment=CENTER))
        
        title_label = toga.Label(
            "📖 Quran App",
            style=Pack(text_align=CENTER, font_size=24, font_weight="bold", padding=20)
        )
        
        self.username_input = toga.TextInput(
            placeholder="Username",
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
        
        main_box.add(title_label)
        main_box.add(self.username_input)
        main_box.add(self.password_input)
        main_box.add(login_btn)
        main_box.add(register_student_btn)
        
        self.main_window.content = main_box
    
    def show_register_student(self, widget):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=30, alignment=CENTER))
        
        title_label = toga.Label(
            "🎓 Register Student",
            style=Pack(text_align=CENTER, font_size=20, font_weight="bold", padding=10)
        )
        
        self.name_input = toga.TextInput(placeholder="Full Name", style=Pack(padding=10))
        self.email_input = toga.TextInput(placeholder="Email", style=Pack(padding=10))
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
    
    def login(self, widget):
        try:
            response = requests.post(
                "https://quran-app-kw38.onrender.com/login",
                json={
                    "username": self.username_input.value,
                    "password": self.password_input.value
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.main_window.info_dialog("Success", "Login successful!")
            else:
                self.main_window.error_dialog("Error", "Login failed!")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")
    
    def register_student(self, widget):
        try:
            response = requests.post(
                "https://quran-app-kw38.onrender.com/register/student",  # با slash
                json={
                    "name": self.name_input.value,
                    "email": self.email_input.value,
                    "password": self.password_input.value,
                    "level": self.level_input.value
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.main_window.info_dialog("Success", "Registration successful!")
                self.show_login_screen()
            else:
                self.main_window.error_dialog("Error", f"Registration failed: {response.text}")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")

def main():
    return QuranApp("Quran App", "com.quranapp.app")

if __name__ == "__main__":
    app = main()
    app.main_loop()
