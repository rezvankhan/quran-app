# Frontend-toga.py - کامل (تصحیح شده)
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import requests
import json

class QuranApp(toga.App):
    def __init__(self):
        super().__init__("Quran App", "com.quranapp.app")
        self.current_user = None
        self.user_token = None
        self.user_role = None
    
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 700))
        self.show_login_screen()
        self.main_window.show()
    
    def show_login_screen(self, widget=None):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=30, alignment=CENTER))
        
        title_label = toga.Label(
            "Quran App",
            style=Pack(text_align=CENTER, font_size=24, font_weight="bold", padding=20)
        )
        
        self.username_input = toga.TextInput(
            placeholder="Username (Teachers) or Email (Students)",
            style=Pack(padding=10, flex=1)
        )
        
        self.password_input = toga.PasswordInput(
            placeholder="Password", 
            style=Pack(padding=10, flex=1)
        )
        
        login_btn = toga.Button(
            "Login",
            on_press=self.login,
            style=Pack(padding=15, background_color="#4CAF50", color="white")
        )
        
        register_student_btn = toga.Button(
            "Register Student",
            on_press=self.show_register_student,
            style=Pack(padding=15, background_color="#2196F3", color="white")
        )
        
        register_teacher_btn = toga.Button(
            "Register Teacher",
            on_press=self.show_register_teacher,
            style=Pack(padding=15, background_color="#FF9800", color="white")
        )
        
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
            "Register Student",
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
            "Register",
            on_press=self.register_student,
            style=Pack(padding=15, background_color="#4CAF50", color="white")
        )
        
        back_btn = toga.Button(
            "Back",
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
            "Register Teacher",
            style=Pack(text_align=CENTER, font_size=20, font_weight="bold", padding=10)
        )
        
        self.teacher_username = toga.TextInput(placeholder="Username", style=Pack(padding=10))
        self.teacher_password = toga.PasswordInput(placeholder="Password", style=Pack(padding=10))
        self.teacher_name = toga.TextInput(placeholder="Full Name", style=Pack(padding=10))
        self.teacher_email = toga.TextInput(placeholder="Email", style=Pack(padding=10))
        self.teacher_specialty = toga.TextInput(placeholder="Specialty", style=Pack(padding=10))
        
        register_btn = toga.Button(
            "Register",
            on_press=self.register_teacher,
            style=Pack(padding=15, background_color="#4CAF50", color="white")
        )
        
        back_btn = toga.Button(
            "Back",
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

    def show_student_dashboard(self, user_data):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        header_box = toga.Box(style=Pack(direction=ROW, padding=10, background_color="#e3f2fd"))
        user_info = toga.Label(
            f"Student: {user_data['full_name']}",
            style=Pack(flex=1, font_size=16, font_weight="bold")
        )
        logout_btn = toga.Button(
            "Logout",
            on_press=self.logout,
            style=Pack(padding=5, background_color="#f44336", color="white")
        )
        header_box.add(user_info)
        header_box.add(logout_btn)
        
        content_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        info_box = toga.Box(style=Pack(direction=COLUMN, padding=10, background_color="#f5f5f5"))
        info_box.add(toga.Label(f"Email: {user_data['email']}", style=Pack(padding=5)))
        info_box.add(toga.Label(f"Student ID: {user_data['id']}", style=Pack(padding=5)))
        content_box.add(info_box)
        
        content_box.add(toga.Button(
            "📚 My Courses", 
            on_press=self.show_student_courses,
            style=Pack(padding=15, margin=5, width=200, background_color="#2196F3", color="white")
        ))
        
        content_box.add(toga.Button(
            "📊 My Progress", 
            on_press=self.show_student_progress,
            style=Pack(padding=15, margin=5, width=200, background_color="#4CAF50", color="white")
        ))
        
        content_box.add(toga.Button(
            "👨‍🏫 Find Teachers", 
            on_press=self.find_teachers,
            style=Pack(padding=15, margin=5, width=200, background_color="#FF9800", color="white")
        ))
        
        content_box.add(toga.Button(
            "📅 My Schedule", 
            on_press=self.show_student_schedule,
            style=Pack(padding=15, margin=5, width=200, background_color="#9C27B0", color="white")
        ))
        
        main_box.add(header_box)
        main_box.add(content_box)
        self.main_window.content = main_box

    def show_teacher_dashboard(self, user_data):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        header_box = toga.Box(style=Pack(direction=ROW, padding=10, background_color="#fff3e0"))
        user_info = toga.Label(
            f"Teacher: {user_data['full_name']}",
            style=Pack(flex=1, font_size=16, font_weight="bold")
        )
        logout_btn = toga.Button(
            "Logout",
            on_press=self.logout,
            style=Pack(padding=5, background_color="#f44336", color="white")
        )
        header_box.add(user_info)
        header_box.add(logout_btn)
        
        content_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        info_box = toga.Box(style=Pack(direction=COLUMN, padding=10, background_color="#f5f5f5"))
        info_box.add(toga.Label(f"Email: {user_data['email']}", style=Pack(padding=5)))
        info_box.add(toga.Label(f"Specialty: {user_data.get('specialty', 'General')}", style=Pack(padding=5)))
        content_box.add(info_box)
        
        content_box.add(toga.Button(
            "📖 My Classes", 
            on_press=self.show_teacher_classes,
            style=Pack(padding=15, margin=5, width=200, background_color="#2196F3", color="white")
        ))
        
        content_box.add(toga.Button(
            "➕ Create Class", 
            on_press=self.create_class,
            style=Pack(padding=15, margin=5, width=200, background_color="#4CAF50", color="white")
        ))
        
        content_box.add(toga.Button(
            "👥 My Students", 
            on_press=self.show_teacher_students,
            style=Pack(padding=15, margin=5, width=200, background_color="#FF9800", color="white")
        ))
        
        content_box.add(toga.Button(
            "📈 Statistics", 
            on_press=self.show_teacher_stats,
            style=Pack(padding=15, margin=5, width=200, background_color="#9C27B0", color="white")
        ))
        
        main_box.add(header_box)
        main_box.add(content_box)
        self.main_window.content = main_box

    def show_student_courses(self, widget):
        try:
            response = requests.get(
                f"https://quran-app-kw38.onrender.com/my-courses/{self.current_user['id']}",
                timeout=30
            )
            
            if response.status_code == 200:
                courses = response.json().get("my_courses", [])
                
                main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
                
                header_box = toga.Box(style=Pack(direction=ROW, padding=10, background_color="#e3f2fd"))
                header_box.add(toga.Label("My Courses", style=Pack(flex=1, font_size=18, font_weight="bold")))
                back_btn = toga.Button("Back", on_press=lambda w: self.show_student_dashboard(self.current_user))
                header_box.add(back_btn)
                main_box.add(header_box)
                
                if courses:
                    for course in courses:
                        course_box = toga.Box(style=Pack(direction=COLUMN, padding=10, background_color="#f5f5f5", margin=5))
                        course_box.add(toga.Label(course["title"], style=Pack(font_weight="bold")))
                        course_box.add(toga.Label(f"Teacher: {course['teacher_name']}", style=Pack(font_size=12)))
                        course_box.add(toga.Label(f"Level: {course['level']}", style=Pack(font_size=12)))
                        course_box.add(toga.Label(f"Progress: {course.get('progress', 0)}%", style=Pack(font_size=12)))
                        main_box.add(course_box)
                else:
                    main_box.add(toga.Label("No courses enrolled yet", style=Pack(padding=20, text_align=CENTER)))
                
                self.main_window.content = main_box
            else:
                self.main_window.error_dialog("Error", "Failed to load courses")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Failed to load courses: {str(e)}")

    def show_student_progress(self, widget):
        self.main_window.info_dialog("Progress", "Your progress report will appear here")

    def find_teachers(self, widget):
        self.main_window.info_dialog("Find Teachers", "Available teachers list will appear here")

    def show_student_schedule(self, widget):
        self.main_window.info_dialog("Schedule", "Your class schedule will appear here")

    def show_teacher_classes(self, widget):
        self.main_window.info_dialog("My Classes", "List of your teaching classes will appear here")

    def create_class(self, widget):
        self.main_window.info_dialog("Create Class", "Class creation form will appear here")

    def show_teacher_students(self, widget):
        self.main_window.info_dialog("My Students", "List of your students will appear here")

    def show_teacher_stats(self, widget):
        self.main_window.info_dialog("Statistics", "Teaching statistics will appear here")

    def login(self, widget):
        try:
            identifier = self.username_input.value.strip()
            password = self.password_input.value
            
            if not identifier or not password:
                self.main_window.error_dialog("Error", "Please enter both username/email and password")
                return
            
            response = requests.post(
                "https://quran-app-kw38.onrender.com/login",
                json={"username": identifier, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Login response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                self.current_user = result['user']
                self.user_role = result['user']['role']
                
                if self.user_role == 'student':
                    self.show_student_dashboard(self.current_user)
                elif self.user_role == 'teacher':
                    self.show_teacher_dashboard(self.current_user)
                else:
                    self.main_window.info_dialog("Success", f"Login successful! Welcome {self.current_user['full_name']}")
                    
            else:
                error_msg = response.json().get("detail", "Login failed")
                self.main_window.error_dialog("Error", f"Login failed: {error_msg}")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")

    def logout(self, widget):
        self.current_user = None
        self.user_token = None
        self.user_role = None
        self.show_login_screen()
        self.main_window.info_dialog("Info", "Logged out successfully")

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
                json={"name": name, "email": email, "password": password, "level": level},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                self.main_window.info_dialog("Success", "Student registration successful! Please login with your email.")
                self.show_login_screen()
            else:
                error_msg = response.json().get("detail", "Registration failed")
                self.main_window.error_dialog("Error", f"Registration failed: {error_msg}")
                
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
                    "username": username, "password": password, 
                    "full_name": full_name, "email": email, "specialty": specialty
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                self.main_window.info_dialog("Success", "Teacher registration successful! Please login with your username.")
                self.show_login_screen()
            else:
                error_msg = response.json().get("detail", "Registration failed")
                self.main_window.error_dialog("Error", f"Registration failed: {error_msg}")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")

def main():
    return QuranApp()

if __name__ == "__main__":
    app = main()
    app.main_loop()
