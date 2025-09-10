# Frontend-toga.py - کامل با همه توابع
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import requests
import json

class QuranApp(toga.App):
    def __init__(self):
        super().__init__(
            "📚 Quran Academy",
            "com.quranapp.app"
        )
        self.current_user = None
        self.user_token = None
        self.user_role = None
    
    def startup(self):
        self.main_window = toga.MainWindow(
            title="📚 Quran Academy - Islamic Learning Platform",
            size=(500, 800)
        )
        self.show_login_screen()
        self.main_window.show()
    
    def show_login_screen(self, widget=None):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=0, alignment=CENTER))
        
        # هدر زیبا با آیکون کتاب بزرگ
        header_box = toga.Box(style=Pack(direction=ROW, padding=25, background_color="#0D8E3D", alignment=CENTER))
        header_icon = toga.Label(
            "📚",
            style=Pack(font_size=32, padding_right=15, color="#87CEEB")
        )
        header_text = toga.Label(
            "QURAN ACADEMY",
            style=Pack(color="blue", font_size=24, font_weight="bold")
        )
        header_box.add(header_icon)
        header_box.add(header_text)
        main_box.add(header_box)
        
        # زیرعنوان
        subtitle_label = toga.Label(
            "Islamic Education Platform",
            style=Pack(text_align=CENTER, font_size=14, color="#0D8E3D", padding=10)
        )
        main_box.add(subtitle_label)
        
        # محتوای اصلی
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

    def show_register_student(self, widget):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=0, alignment=CENTER))
        
        # هدر
        header_box = toga.Box(style=Pack(direction=ROW, padding=20, background_color="#2196F3", alignment=CENTER))
        header_icon = toga.Label(
            "👨‍🎓",
            style=Pack(font_size=28, padding_right=10, color="white")
        )
        header_text = toga.Label(
            "Student Registration",
            style=Pack(color="white", font_size=20, font_weight="bold")
        )
        header_box.add(header_icon)
        header_box.add(header_text)
        main_box.add(header_box)
        
        # محتوا
        content_box = toga.Box(style=Pack(direction=COLUMN, padding=25, alignment=CENTER))
        
        self.name_input = toga.TextInput(
            placeholder="Full Name", 
            style=Pack(padding=10, width=300, background_color="#f8f9fa")
        )
        self.email_input = toga.TextInput(
            placeholder="Email Address", 
            style=Pack(padding=10, width=300, background_color="#f8f9fa")
        )
        self.password_input = toga.PasswordInput(
            placeholder="Password", 
            style=Pack(padding=10, width=300, background_color="#f8f9fa")
        )
        self.level_input = toga.Selection(
            items=["Beginner", "Intermediate", "Advanced"],
            style=Pack(padding=10, width=300)
        )
        
        register_btn = toga.Button(
            "🚀 Create Student Account",
            on_press=self.register_student,
            style=Pack(padding=15, background_color="#2196F3", color="white", width=250, font_weight="bold")
        )
        
        back_btn = toga.Button(
            "⬅ Back to Login",
            on_press=self.show_login_screen,
            style=Pack(padding=10, background_color="#6c757d", color="white", width=180)
        )
        
        content_box.add(self.name_input)
        content_box.add(self.email_input)
        content_box.add(self.password_input)
        content_box.add(self.level_input)
        content_box.add(register_btn)
        content_box.add(back_btn)
        
        main_box.add(content_box)
        self.main_window.content = main_box

    def show_register_teacher(self, widget):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=0, alignment=CENTER))
        
        # هدر
        header_box = toga.Box(style=Pack(direction=ROW, padding=20, background_color="#FF9800", alignment=CENTER))
        header_icon = toga.Label(
            "👨‍🏫",
            style=Pack(font_size=28, padding_right=10, color="white")
        )
        header_text = toga.Label(
            "Teacher Registration",
            style=Pack(color="white", font_size=20, font_weight="bold")
        )
        header_box.add(header_icon)
        header_box.add(header_text)
        main_box.add(header_box)
        
        # محتوا
        content_box = toga.Box(style=Pack(direction=COLUMN, padding=25, alignment=CENTER))
        
        self.teacher_username = toga.TextInput(
            placeholder="Username", 
            style=Pack(padding=10, width=300, background_color="#f8f9fa")
        )
        self.teacher_password = toga.PasswordInput(
            placeholder="Password", 
            style=Pack(padding=10, width=300, background_color="#f8f9fa")
        )
        self.teacher_name = toga.TextInput(
            placeholder="Full Name", 
            style=Pack(padding=10, width=300, background_color="#f8f9fa")
        )
        self.teacher_email = toga.TextInput(
            placeholder="Email Address", 
            style=Pack(padding=10, width=300, background_color="#f8f9fa")
        )
        self.teacher_specialty = toga.TextInput(
            placeholder="Specialty (e.g., Tajweed, Recitation)", 
            style=Pack(padding=10, width=300, background_color="#f8f9fa")
        )
        
        register_btn = toga.Button(
            "🚀 Create Teacher Account",
            on_press=self.register_teacher,
            style=Pack(padding=15, background_color="#FF9800", color="white", width=250, font_weight="bold")
        )
        
        back_btn = toga.Button(
            "⬅ Back to Login",
            on_press=self.show_login_screen,
            style=Pack(padding=10, background_color="#6c757d", color="white", width=180)
        )
        
        content_box.add(self.teacher_username)
        content_box.add(self.teacher_password)
        content_box.add(self.teacher_name)
        content_box.add(self.teacher_email)
        content_box.add(self.teacher_specialty)
        content_box.add(register_btn)
        content_box.add(back_btn)
        
        main_box.add(content_box)
        self.main_window.content = main_box

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

    def show_teacher_dashboard(self, user_data):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=0, alignment=CENTER))
        
        # هدر
        header_box = toga.Box(style=Pack(direction=ROW, padding=15, background_color="#FF9800", alignment=CENTER))
        header_icon = toga.Label(
            "👨‍🏫",
            style=Pack(font_size=24, padding_right=10, color="white")
        )
        header_text = toga.Label(
            f"Teacher: {user_data['full_name']}",
            style=Pack(color="white", font_size=18, font_weight="bold", flex=1)
        )
        logout_btn = toga.Button(
            "🚪 Logout",
            on_press=self.logout,
            style=Pack(padding=8, background_color="#f44336", color="white")
        )
        header_box.add(header_icon)
        header_box.add(header_text)
        header_box.add(logout_btn)
        main_box.add(header_box)
        
        content_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        info_box = toga.Box(style=Pack(direction=COLUMN, padding=10, background_color="#f5f5f5"))
        info_box.add(toga.Label(f"📧 Email: {user_data['email']}", style=Pack(padding=5)))
        info_box.add(toga.Label(f"🎯 Specialty: {user_data.get('specialty', 'General')}", style=Pack(padding=5)))
        content_box.add(info_box)
        
        quran_types_label = toga.Label(
            "Select Quran Course Type:",
            style=Pack(padding=10, font_weight="bold")
        )
        
        self.quran_type_combo = toga.Selection(
            items=[
                "Tajweed Fundamentals",
                "Quran Recitation (Tartil)",
                "Quran Recitation (Tahqeeq)",
                "Quran Recitation (Tadweer)",
                "Quran Memorization (Hifz)",
                "Quran Tafsir",
                "Quran Translation",
                "Arabic Pronunciation",
                "Voice and Melody"
            ],
            style=Pack(padding=10, width=250)
        )
        
        content_box.add(quran_types_label)
        content_box.add(self.quran_type_combo)
        
        content_box.add(toga.Button(
            "📖 My Classes", 
            on_press=self.show_teacher_classes,
            style=Pack(padding=15, width=200, background_color="#2196F3", color="white")
        ))
        
        content_box.add(toga.Button(
            "➕ Create New Course", 
            on_press=self.create_class,
            style=Pack(padding=15, width=200, background_color="#4CAF50", color="white")
        ))
        
        content_box.add(toga.Button(
            "👥 My Students", 
            on_press=self.show_teacher_students,
            style=Pack(padding=15, width=200, background_color="#FF9800", color="white")
        ))
        
        content_box.add(toga.Button(
            "📈 Statistics", 
            on_press=self.show_teacher_stats,
            style=Pack(padding=15, width=200, background_color="#9C27B0", color="white")
        ))
        
        main_box.add(content_box)
        self.main_window.content = main_box

    def show_student_dashboard(self, user_data):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=0, alignment=CENTER))
        
        # هدر
        header_box = toga.Box(style=Pack(direction=ROW, padding=15, background_color="#2196F3", alignment=CENTER))
        header_icon = toga.Label(
            "👨‍🎓",
            style=Pack(font_size=24, padding_right=10, color="white")
        )
        header_text = toga.Label(
            f"Student: {user_data['full_name']}",
            style=Pack(color="white", font_size=18, font_weight="bold", flex=1)
        )
        logout_btn = toga.Button(
            "🚪 Logout",
            on_press=self.logout,
            style=Pack(padding=8, background_color="#f44336", color="white")
        )
        header_box.add(header_icon)
        header_box.add(header_text)
        header_box.add(logout_btn)
        main_box.add(header_box)
        
        content_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        info_box = toga.Box(style=Pack(direction=COLUMN, padding=10, background_color="#f5f5f5"))
        info_box.add(toga.Label(f"📧 Email: {user_data['email']}", style=Pack(padding=5)))
        info_box.add(toga.Label(f"🆔 Student ID: {user_data['id']}", style=Pack(padding=5)))
        content_box.add(info_box)
        
        content_box.add(toga.Button(
            "📚 My Courses", 
            on_press=self.show_student_courses,
            style=Pack(padding=15, width=200, background_color="#2196F3", color="white")
        ))
        
        content_box.add(toga.Button(
            "📊 My Progress", 
            on_press=self.show_student_progress,
            style=Pack(padding=15, width=200, background_color="#4CAF50", color="white")
        ))
        
        content_box.add(toga.Button(
            "👨‍🏫 Find Teachers", 
            on_press=self.find_teachers,
            style=Pack(padding=15, width=200, background_color="#FF9800", color="white")
        ))
        
        content_box.add(toga.Button(
            "📅 My Schedule", 
            on_press=self.show_student_schedule,
            style=Pack(padding=15, width=200, background_color="#9C27B0", color="white")
        ))
        
        main_box.add(content_box)
        self.main_window.content = main_box

    def show_student_courses(self, widget):
        self.main_window.info_dialog("My Courses", "List of your courses will appear here")

    def show_student_progress(self, widget):
        self.main_window.info_dialog("Progress", "Your progress report will appear here")

    def find_teachers(self, widget):
        self.main_window.info_dialog("Find Teachers", "Available teachers list will appear here")

    def show_student_schedule(self, widget):
        self.main_window.info_dialog("Schedule", "Your class schedule will appear here")

    def show_teacher_classes(self, widget):
        self.main_window.info_dialog("My Classes", "List of your teaching classes will appear here")

    def create_class(self, widget):
        try:
            selected_type = self.quran_type_combo.value
            if not selected_type:
                self.main_window.info_dialog("Error", "Please select a Quran course type")
                return
            
            self.show_create_course_form(selected_type)
            
        except Exception as e:
            self.main_window.error_dialog("Error", f"Error creating course: {str(e)}")

    def show_create_course_form(self, course_type):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        header_box = toga.Box(style=Pack(direction=ROW, padding=10, background_color="#e3f2fd"))
        header_box.add(toga.Label(f"Create New Course - {course_type}", style=Pack(flex=1, font_size=18, font_weight="bold")))
        back_btn = toga.Button("Back", on_press=lambda w: self.show_teacher_dashboard(self.current_user))
        header_box.add(back_btn)
        main_box.add(header_box)
        
        form_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        form_box.add(toga.Label("Course Title:", style=Pack(padding=5)))
        self.course_title = toga.TextInput(placeholder="Course title", style=Pack(padding=5))
        form_box.add(self.course_title)
        
        form_box.add(toga.Label("Description:", style=Pack(padding=5)))
        self.course_description = toga.MultilineTextInput(placeholder="Course description", style=Pack(padding=5, height=100))
        form_box.add(self.course_description)
        
        form_box.add(toga.Label("Level:", style=Pack(padding=5)))
        self.course_level = toga.Selection(
            items=["Beginner", "Intermediate", "Advanced"],
            style=Pack(padding=5)
        )
        form_box.add(self.course_level)
        
        form_box.add(toga.Label("Duration (minutes):", style=Pack(padding=5)))
        self.course_duration = toga.NumberInput(min_value=30, max_value=180, value=60, style=Pack(padding=5))
        form_box.add(self.course_duration)
        
        form_box.add(toga.Label("Max Students:", style=Pack(padding=5)))
        self.course_capacity = toga.NumberInput(min_value=1, max_value=50, value=10, style=Pack(padding=5))
        form_box.add(self.course_capacity)
        
        form_box.add(toga.Label("Schedule:", style=Pack(padding=5)))
        self.course_schedule = toga.TextInput(placeholder="e.g., Monday & Wednesday 18-20", style=Pack(padding=5))
        form_box.add(self.course_schedule)
        
        create_btn = toga.Button(
            "Create Course",
            on_press=lambda w: self.submit_course(course_type),
            style=Pack(padding=15, background_color="#4CAF50", color="white")
        )
        form_box.add(create_btn)
        
        main_box.add(form_box)
        self.main_window.content = main_box

    def submit_course(self, course_type):
        try:
            course_data = {
                "title": self.course_title.value,
                "description": self.course_description.value,
                "level": self.course_level.value,
                "category": course_type,
                "duration": int(self.course_duration.value),
                "max_students": int(self.course_capacity.value),
                "schedule": self.course_schedule.value,
                "price": 0
            }
            
            response = requests.post(
                "https://quran-app-kw38.onrender.com/teacher/courses",
                json=course_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                self.main_window.info_dialog("Success", "Course created successfully!")
                self.show_teacher_dashboard(self.current_user)
            else:
                error_msg = response.json().get("detail", "Error creating course")
                self.main_window.error_dialog("Error", error_msg)
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Error creating course: {str(e)}")

    def show_teacher_students(self, widget):
        self.main_window.info_dialog("My Students", "List of your students will appear here")

    def show_teacher_stats(self, widget):
        self.main_window.info_dialog("Statistics", "Teaching statistics will appear here")

def main():
    return QuranApp()

if __name__ == "__main__":
    app = main()
    app.main_loop()
