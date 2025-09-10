# Frontend-toga.py - کامل (نسخه حرفه‌ای با تب)
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
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # هدر برنامه
        header_box = toga.Box(style=Pack(direction=ROW, padding=10, background_color="#2E7D32"))
        title_label = toga.Label(
            "📖 Quran Academy",
            style=Pack(color="white", font_size=20, font_weight="bold", padding=10)
        )
        header_box.add(title_label)
        main_box.add(header_box)
        
        # تب‌های اصلی
        self.tab_view = toga.OptionContainer(style=Pack(flex=1))
        
        # تب LOGIN
        login_box = toga.Box(style=Pack(direction=COLUMN, padding=30, alignment=CENTER))
        
        login_box.add(toga.Label(
            "Login to Your Account",
            style=Pack(text_align=CENTER, font_size=18, font_weight="bold", padding=20, color="#2E7D32")
        ))
        
        self.login_username = toga.TextInput(
            placeholder="Username (Teachers) or Email (Students)",
            style=Pack(padding=10, flex=1)
        )
        
        self.login_password = toga.PasswordInput(
            placeholder="Password", 
            style=Pack(padding=10, flex=1)
        )
        
        login_btn = toga.Button(
            "🔐 Login",
            on_press=self.login,
            style=Pack(padding=15, background_color="#2E7D32", color="white", width=200)
        )
        
        login_help = toga.Label(
            "Note: Students login with email, Teachers with username",
            style=Pack(text_align=CENTER, font_size=10, color="gray", padding=10)
        )
        
        login_box.add(self.login_username)
        login_box.add(self.login_password)
        login_box.add(login_btn)
        login_box.add(login_help)
        
        # تب REGISTER
        register_box = toga.Box(style=Pack(direction=COLUMN, padding=30, alignment=CENTER))
        
        register_box.add(toga.Label(
            "Create New Account",
            style=Pack(text_align=CENTER, font_size=18, font_weight="bold", padding=20, color="#1565C0")
        ))
        
        self.reg_type = toga.Selection(
            items=["Select Account Type", "Student", "Teacher"],
            style=Pack(padding=10, width=250)
        )
        
        self.reg_fullname = toga.TextInput(
            placeholder="Full Name",
            style=Pack(padding=10)
        )
        
        self.reg_email = toga.TextInput(
            placeholder="Email Address",
            style=Pack(padding=10)
        )
        
        self.reg_username = toga.TextInput(
            placeholder="Username (for Teachers)",
            style=Pack(padding=10)
        )
        
        self.reg_password = toga.PasswordInput(
            placeholder="Password",
            style=Pack(padding=10)
        )
        
        self.reg_specialty = toga.TextInput(
            placeholder="Specialty (for Teachers)",
            style=Pack(padding=10)
        )
        
        self.reg_level = toga.Selection(
            items=["Beginner", "Intermediate", "Advanced"],
            style=Pack(padding=10)
        )
        
        register_btn = toga.Button(
            "🚀 Create Account",
            on_press=self.handle_registration,
            style=Pack(padding=15, background_color="#1565C0", color="white", width=200)
        )
        
        # ابتدا فیلدها را مخفی می‌کنیم
        self.reg_fullname.visible = False
        self.reg_email.visible = False
        self.reg_username.visible = False
        self.reg_password.visible = False
        self.reg_specialty.visible = False
        self.reg_level.visible = False
        register_btn.visible = False
        
        register_box.add(self.reg_type)
        register_box.add(self.reg_fullname)
        register_box.add(self.reg_email)
        register_box.add(self.reg_username)
        register_box.add(self.reg_password)
        register_box.add(self.reg_specialty)
        register_box.add(self.reg_level)
        register_box.add(register_btn)
        
        # اضافه کردن تب‌ها
        self.tab_view.add("🔐 Login", login_box)
        self.tab_view.add("🚀 Register", register_box)
        
        main_box.add(self.tab_view)
        
        # رویداد تغییر نوع ثبت نام
        self.reg_type.on_change = self.on_reg_type_change
        
        self.main_window.content = main_box
    
    def on_reg_type_change(self, widget):
        # نمایش فیلدهای مناسب بر اساس نوع کاربر
        is_teacher = self.reg_type.value == "Teacher"
        is_student = self.reg_type.value == "Student"
        is_selected = is_teacher or is_student
        
        self.reg_fullname.visible = is_selected
        self.reg_email.visible = is_selected
        self.reg_password.visible = is_selected
        self.reg_username.visible = is_teacher
        self.reg_specialty.visible = is_teacher
        self.reg_level.visible = is_student
        
        register_btn = widget.parent.children[-1]  # آخرین فرزند که دکمه ثبت نام است
        register_btn.visible = is_selected
    
    def handle_registration(self, widget):
        account_type = self.reg_type.value
        
        if account_type == "Student":
            self.register_student(widget)
        elif account_type == "Teacher":
            self.register_teacher(widget)
        else:
            self.main_window.info_dialog("Info", "Please select an account type")
    
    def register_student(self, widget):
        try:
            name = self.reg_fullname.value.strip()
            email = self.reg_email.value.strip()
            password = self.reg_password.value
            level = self.reg_level.value
            
            if not all([name, email, password, level]):
                self.main_window.error_dialog("Error", "Please fill all required fields")
                return
            
            response = requests.post(
                "https://quran-app-kw38.onrender.com/register/student",
                json={"name": name, "email": email, "password": password, "level": level},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                self.main_window.info_dialog("Success", "Student account created successfully! Please login with your email.")
                self.tab_view.content = 0  # بازگشت به تب Login
                self.clear_registration_form()
            else:
                error_msg = response.json().get("detail", "Registration failed")
                self.main_window.error_dialog("Error", f"Registration failed: {error_msg}")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")
    
    def register_teacher(self, widget):
        try:
            username = self.reg_username.value.strip()
            password = self.reg_password.value
            full_name = self.reg_fullname.value.strip()
            email = self.reg_email.value.strip()
            specialty = self.reg_specialty.value.strip()
            
            if not all([username, password, full_name, email, specialty]):
                self.main_window.error_dialog("Error", "Please fill all required fields")
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
                self.main_window.info_dialog("Success", "Teacher account created successfully! Please login with your username.")
                self.tab_view.content = 0  # بازگشت به تب Login
                self.clear_registration_form()
            else:
                error_msg = response.json().get("detail", "Registration failed")
                self.main_window.error_dialog("Error", f"Registration failed: {error_msg}")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")
    
    def clear_registration_form(self):
        # پاک کردن تمام فیلدهای فرم
        self.reg_type.value = "Select Account Type"
        self.reg_fullname.value = ""
        self.reg_email.value = ""
        self.reg_username.value = ""
        self.reg_password.value = ""
        self.reg_specialty.value = ""
        self.reg_level.value = "Beginner"
        
        # مخفی کردن فیلدها
        self.reg_fullname.visible = False
        self.reg_email.visible = False
        self.reg_username.visible = False
        self.reg_password.visible = False
        self.reg_specialty.visible = False
        self.reg_level.visible = False
        
        # مخفی کردن دکمه
        for child in self.reg_level.parent.children:
            if isinstance(child, toga.Button):
                child.visible = False

    def show_teacher_dashboard(self, user_data):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        header_box = toga.Box(style=Pack(direction=ROW, padding=10, background_color="#fff3e0"))
        user_info = toga.Label(
            f"👨‍🏫 Teacher: {user_data['full_name']}",
            style=Pack(flex=1, font_size=16, font_weight="bold")
        )
        logout_btn = toga.Button(
            "🚪 Logout",
            on_press=self.logout,
            style=Pack(padding=5, background_color="#f44336", color="white")
        )
        header_box.add(user_info)
        header_box.add(logout_btn)
        
        content_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        info_box = toga.Box(style=Pack(direction=COLUMN, padding=10, background_color="#f5f5f5"))
        info_box.add(toga.Label(f"📧 Email: {user_data['email']}", style=Pack(padding=5)))
        info_box.add(toga.Label(f"🎯 Specialty: {user_data.get('specialty', 'General')}", style=Pack(padding=5)))
        content_box.add(info_box)
        
        # Quran Course Types ComboBox
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
        
        main_box.add(header_box)
        main_box.add(content_box)
        self.main_window.content = main_box

    def show_student_dashboard(self, user_data):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        header_box = toga.Box(style=Pack(direction=ROW, padding=10, background_color="#e3f2fd"))
        user_info = toga.Label(
            f"👨‍🎓 Student: {user_data['full_name']}",
            style=Pack(flex=1, font_size=16, font_weight="bold")
        )
        logout_btn = toga.Button(
            "🚪 Logout",
            on_press=self.logout,
            style=Pack(padding=5, background_color="#f44336", color="white")
        )
        header_box.add(user_info)
        header_box.add(logout_btn)
        
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
        
        main_box.add(header_box)
        main_box.add(content_box)
        self.main_window.content = main_box

    def login(self, widget):
        try:
            identifier = self.login_username.value.strip()
            password = self.login_password.value
            
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

    # بقیه توابع بدون تغییر می‌مانند...
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
