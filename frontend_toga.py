# Frontend-toga.py - کامل با کیف پول و آزمون
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
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
        self.BASE_URL = "https://quran-app-kw38.onrender.com"
        print(f"🔗 Connecting to backend: {self.BASE_URL}")
        
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
        self.main_window.info_dialog("Info", "Logged out successfully")
    
    def make_authenticated_request(self, method, endpoint, **kwargs):
        if not self.is_token_valid():
            self.main_window.info_dialog("Session Expired", "Please login again")
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
            self.main_window.error_dialog("Connection Error", 
                f"Cannot connect to server at {self.BASE_URL}. Please check if the backend is running.")
            return None
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")
            return None
    
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
        
        status_label = toga.Label(
            f"Connected to: {self.BASE_URL}",
            style=Pack(text_align=CENTER, font_size=10, color="#666", padding=5)
        )
        main_box.add(status_label)
        
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
                f"{self.BASE_URL}/register/student",
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
                f"{self.BASE_URL}/register/teacher",
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

    def login(self, widget):
        try:
            identifier = self.username_input.value.strip()
            password = self.password_input.value
            
            if not identifier or not password:
                self.main_window.error_dialog("Error", "Please enter both username/email and password")
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
                        self.main_window.info_dialog("Success", f"Login successful! Welcome {user_data['full_name']}")
                else:
                    self.main_window.error_dialog("Error", "Failed to get user information")
                    
            else:
                error_msg = response.json().get("detail", "Login failed")
                self.main_window.error_dialog("Error", f"Login failed: {error_msg}")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Connection error: {str(e)}")

    def show_teacher_dashboard(self, user_data):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=0, alignment=CENTER))
        
        header_box = toga.Box(style=Pack(direction=ROW, padding=15, background_color="#0D8E3D", alignment=CENTER))
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
        info_box.add(toga.Label(f"💰 Wallet: ${user_data.get('wallet_balance', 0)}", style=Pack(padding=5)))
        content_box.add(info_box)
        
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
            "💰 Wallet Management", 
            on_press=self.show_wallet,
            style=Pack(padding=15, width=200, background_color="#607D8B", color="white")
        ))
        
        content_box.add(toga.Button(
            "📝 Create Exam", 
            on_press=self.create_exam,
            style=Pack(padding=15, width=200, background_color="#795548", color="white")
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
        
        header_box = toga.Box(style=Pack(direction=ROW, padding=15, background_color="#0D8E3D", alignment=CENTER))
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
        info_box.add(toga.Label(f"💰 Wallet: ${user_data.get('wallet_balance', 0)}", style=Pack(padding=5)))
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
            "💰 My Wallet", 
            on_press=self.show_wallet,
            style=Pack(padding=15, width=200, background_color="#607D8B", color="white")
        ))
        
        content_box.add(toga.Button(
            "📝 Class Exams", 
            on_press=self.show_exams,
            style=Pack(padding=15, width=200, background_color="#795548", color="white")
        ))
        
        content_box.add(toga.Button(
            "📅 My Schedule", 
            on_press=self.show_student_schedule,
            style=Pack(padding=15, width=200, background_color="#9C27B0", color="white")
        ))
        
        main_box.add(content_box)
        self.main_window.content = main_box

    def show_wallet(self, widget):
        response = self.make_authenticated_request("GET", "/wallet/balance")
        if response and response.status_code == 200:
            balance = response.json().get('balance', 0)
        
            # ایجاد صفحه کیف پول
            main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
            header_box = toga.Box(style=Pack(direction=ROW, padding=15, background_color="#607D8B", alignment=CENTER))
            header_icon = toga.Label("💰", style=Pack(font_size=24, padding_right=10, color="white"))
            header_text = toga.Label("Wallet Management", style=Pack(color="white", font_size=18, font_weight="bold"))
            header_box.add(header_icon)
            header_box.add(header_text)
            main_box.add(header_box)
        
            balance_label = toga.Label(f"Current Balance: ${balance}", 
                                 style=Pack(padding=20, font_size=16, font_weight="bold"))
            main_box.add(balance_label)
        
            # فیلد مقدار واریزی
            amount_label = toga.Label("Amount to deposit:", style=Pack(padding=5))
            self.deposit_amount = toga.NumberInput(value=10, style=Pack(padding=10, width=200))
        
            deposit_btn = toga.Button("💳 Deposit", 
                                on_press=self.deposit_money,
                                style=Pack(padding=15, background_color="#4CAF50", color="white", width=180))
        
            back_btn = toga.Button("⬅ Back", 
                             on_press=lambda w: self.show_teacher_dashboard(self.current_user) if self.user_role == 'teacher' else self.show_student_dashboard(self.current_user),
                             style=Pack(padding=10, background_color="#6c757d", color="white", width=120))
        
            main_box.add(amount_label)
            main_box.add(self.deposit_amount)
            main_box.add(deposit_btn)
            main_box.add(back_btn)
        
            self.main_window.content = main_box
        else:
            self.main_window.error_dialog("Error", "Failed to load wallet balance")
    
    def create_exam(self, widget):
        # ابتدا دوره‌های معلم را بگیر
        response = self.make_authenticated_request("GET", "/teacher/courses")
        if response and response.status_code == 200:
            courses = response.json().get('courses', [])
            self.show_exam_creation_form(courses)
        else:
            self.main_window.error_dialog("Error", "Failed to load courses")
        
    def show_exam_creation_form(self, courses):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
    
        header_box = toga.Box(style=Pack(direction=ROW, padding=15, background_color="#795548", alignment=CENTER))
        header_icon = toga.Label("📝", style=Pack(font_size=24, padding_right=10, color="white"))
        header_text = toga.Label("Create New Exam", style=Pack(color="white", font_size=18, font_weight="bold"))
        header_box.add(header_icon)
        header_box.add(header_text)
        main_box.add(header_box)
    
        # انتخاب دوره
        course_label = toga.Label("Select Course:", style=Pack(padding=10))
        course_options = [f"{course['id']} - {course['title']}" for course in courses]
        self.course_selection = toga.Selection(items=course_options, style=Pack(padding=10, width=300))
    
        # فیلدهای آزمون
        title_label = toga.Label("Exam Title:", style=Pack(padding=5))
        self.exam_title = toga.TextInput(placeholder="Enter exam title", style=Pack(padding=10))
    
        desc_label = toga.Label("Description:", style=Pack(padding=5))
        self.exam_description = toga.TextInput(placeholder="Enter description", style=Pack(padding=10))
    
        create_btn = toga.Button("Create Exam", 
                           on_press=self.submit_exam,
                           style=Pack(padding=15, background_color="#795548", color="white", width=180))
    
        back_btn = toga.Button("⬅ Back", 
                         on_press=lambda w: self.show_teacher_dashboard(self.current_user),
                         style=Pack(padding=10, background_color="#6c757d", color="white", width=120))
    
        main_box.add(course_label)
        main_box.add(self.course_selection)
        main_box.add(title_label)
        main_box.add(self.exam_title)
        main_box.add(desc_label)
        main_box.add(self.exam_description)
        main_box.add(create_btn)
        main_box.add(back_btn)
        
        self.main_window.content = main_box

    def submit_exam(self, widget):
        try:
            selected_course = self.course_selection.value
            course_id = selected_course.split(" - ")[0] if selected_course else None
            title = self.exam_title.value.strip()
            description = self.exam_description.value.strip()
            
            if not all([course_id, title]):
                self.main_window.error_dialog("Error", "Please select a course and enter a title")
                return
            
            response = self.make_authenticated_request(
                "POST", 
                "/exams/create",
                json={
                    "course_id": course_id,
                    "title": title,
                    "description": description
                }
            )
            
            if response and response.status_code == 200:
                self.main_window.info_dialog("Success", "Exam created successfully!")
                self.show_teacher_dashboard(self.current_user)
            else:
                self.main_window.error_dialog("Error", "Failed to create exam")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Exam creation error: {str(e)}")

    def deposit_money(self, widget):
        try:
            amount = self.deposit_amount.value
            if not amount or amount <= 0:
                self.main_window.error_dialog("Error", "Please enter a valid amount")
                return
        
            response = self.make_authenticated_request("POST", "/wallet/deposit", 
                                                 json={"amount": amount, "description": "Deposit from app"})
        
            if response and response.status_code == 200:
                new_balance = response.json().get('new_balance', 0)
                self.main_window.info_dialog("Success", f"Deposit successful!\nNew balance: ${new_balance}")
                # بازگشت به dashboard
                if self.user_role == 'teacher':
                    self.show_teacher_dashboard(self.current_user)
                else:
                    self.show_student_dashboard(self.current_user)
            else:
                self.main_window.error_dialog("Error", "Deposit failed")
            
        except Exception as e:
            self.main_window.error_dialog("Error", f"Deposit error: {str(e)}")

    def show_student_courses(self, widget):
        response = self.make_authenticated_request("GET", "/my-courses")
        if response and response.status_code == 200:
            courses = response.json().get('my_courses', [])
            courses_list = "\n".join([f"📖 {course['title']} - Progress: {course.get('progress', 0)}%" for course in courses])
            self.main_window.info_dialog("My Courses", courses_list or "No courses enrolled")
        else:
            self.main_window.error_dialog("Error", "Failed to load courses")

    def show_teacher_classes(self, widget):
        response = self.make_authenticated_request("GET", "/teacher/courses")
        if response and response.status_code == 200:
            courses = response.json().get('courses', [])
            courses_list = "\n".join([f"🎯 {course['title']} - Students: {course.get('enrolled_students', 0)}" for course in courses])
            self.main_window.info_dialog("My Classes", courses_list or "No classes created")
        else:
            self.main_window.error_dialog("Error", "Failed to load classes")

    def create_class(self, widget):
        # Create a form for class creation
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        header_box = toga.Box(style=Pack(direction=ROW, padding=15, background_color="#4CAF50", alignment=CENTER))
        header_icon = toga.Label("➕", style=Pack(font_size=24, padding_right=10, color="white"))
        header_text = toga.Label("Create New Course", style=Pack(color="white", font_size=18, font_weight="bold"))
        header_box.add(header_icon)
        header_box.add(header_text)
        main_box.add(header_box)
        
        # Form fields
        title_label = toga.Label("Course Title:", style=Pack(padding=5))
        self.course_title = toga.TextInput(placeholder="Enter course title", style=Pack(padding=10))
        
        desc_label = toga.Label("Description:", style=Pack(padding=5))
        self.course_description = toga.TextInput(placeholder="Enter course description", style=Pack(padding=10))
        
        price_label = toga.Label("Price ($):", style=Pack(padding=5))
        self.course_price = toga.NumberInput(value=0, style=Pack(padding=10))
        
        create_btn = toga.Button("Create Course", 
                           on_press=self.submit_course,
                           style=Pack(padding=15, background_color="#4CAF50", color="white", width=180))
        
        back_btn = toga.Button("⬅ Back", 
                         on_press=lambda w: self.show_teacher_dashboard(self.current_user),
                         style=Pack(padding=10, background_color="#6c757d", color="white", width=120))
        
        main_box.add(title_label)
        main_box.add(self.course_title)
        main_box.add(desc_label)
        main_box.add(self.course_description)
        main_box.add(price_label)
        main_box.add(self.course_price)
        main_box.add(create_btn)
        main_box.add(back_btn)
        
        self.main_window.content = main_box

    def submit_course(self, widget):
        try:
            title = self.course_title.value.strip()
            description = self.course_description.value.strip()
            price = self.course_price.value
            
            if not title:
                self.main_window.error_dialog("Error", "Please enter a course title")
                return
            
            response = self.make_authenticated_request(
                "POST", 
                "/courses/create",
                json={
                    "title": title,
                    "description": description,
                    "price": price
                }
            )
            
            if response and response.status_code == 200:
                self.main_window.info_dialog("Success", "Course created successfully!")
                self.show_teacher_dashboard(self.current_user)
            else:
                self.main_window.error_dialog("Error", "Failed to create course")
                
        except Exception as e:
            self.main_window.error_dialog("Error", f"Course creation error: {str(e)}")

    def show_student_progress(self, widget):
        response = self.make_authenticated_request("GET", "/my-courses")
        if response and response.status_code == 200:
            courses = response.json().get('my_courses', [])
            progress_text = "\n".join([f"📊 {course['title']}: {course.get('progress', 0)}%" for course in courses])
            self.main_window.info_dialog("My Progress", progress_text or "No progress data available")
        else:
            self.main_window.error_dialog("Error", "Failed to load progress data")

    def find_teachers(self, widget):
        response = requests.get(f"{self.BASE_URL}/users")
        if response and response.status_code == 200:
            users = response.json().get('users', [])
            teachers = [user for user in users if user.get('role') == 'teacher']
            teachers_list = "\n".join([f"👨‍🏫 {teacher['full_name']} - {teacher.get('specialty', 'General')}" for teacher in teachers])
            self.main_window.info_dialog("Available Teachers", teachers_list or "No teachers available")
        else:
            self.main_window.error_dialog("Error", "Failed to load teachers list")

    def show_exams(self, widget):
        response = self.make_authenticated_request("GET", "/my-exams")
        if response and response.status_code == 200:
            exams = response.json().get('exams', [])
            exams_list = "\n".join([f"📝 {exam['title']} - Course: {exam.get('course_title', 'Unknown')}" for exam in exams])
            self.main_window.info_dialog("My Exams", exams_list or "No exams available")
        else:
            self.main_window.error_dialog("Error", "Failed to load exams")

    def show_student_schedule(self, widget):
        response = self.make_authenticated_request("GET", "/my-courses")
        if response and response.status_code == 200:
            courses = response.json().get('my_courses', [])
            schedule_text = "\n".join([f"📅 {course['title']}: {course.get('schedule', 'No schedule')}" for course in courses])
            self.main_window.info_dialog("My Schedule", schedule_text or "No schedule available")
        else:
            self.main_window.error_dialog("Error", "Failed to load schedule")

    def show_teacher_students(self, widget):
        response = self.make_authenticated_request("GET", "/teacher/courses")
        if response and response.status_code == 200:
            courses = response.json().get('courses', [])
            students_info = []
            for course in courses:
                students_info.append(f"📚 {course['title']}: {course.get('enrolled_students', 0)} students")
            self.main_window.info_dialog("My Students", "\n".join(students_info) or "No students enrolled")
        else:
            self.main_window.error_dialog("Error", "Failed to load students information")

    def show_teacher_stats(self, widget):
        response = self.make_authenticated_request("GET", "/teacher/courses")
        if response and response.status_code == 200:
            courses = response.json().get('courses', [])
            total_students = sum(course.get('enrolled_students', 0) for course in courses)
            total_courses = len(courses)
            total_income = sum(course.get('price', 0) * course.get('enrolled_students', 0) for course in courses)
            
            stats_text = f"""📊 Teaching Statistics:

Total Courses: {total_courses}
Total Students: {total_students}
Estimated Income: ${total_income}
"""
            self.main_window.info_dialog("Statistics", stats_text)
        else:
            self.main_window.error_dialog("Error", "Failed to load statistics")

def main():
    return QuranApp()

if __name__ == "__main__":
    app = main()
    app.main_loop()
