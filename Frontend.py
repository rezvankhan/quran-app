import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import requests
import ssl
import urllib3
import json
import asyncio
import warnings
import base64
import threading
from datetime import datetime

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Base API URL
BASE_URL = "https://quran-app-kw38.onrender.com"

# App theme
APP_LOGO = "🕌"
THEME_COLORS = {
    "primary": "#4CAF50",
    "secondary": "#2196F3", 
    "accent": "#FF9800",
    "danger": "#f44336",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "info": "#2196F3"
}

class QuranApp(toga.App):
    def __init__(self):
        super().__init__('Quran App', 'com.quran.app')
        self.token = None
        self.user = None
        self.current_screen = "login"
        self.ws_connections = {}
    
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name, size=(500, 800))
        self.show_login_screen()
        self.main_window.show()
    
    def show_login_screen(self):
        self.current_screen = "login"
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=30, flex=1))
        
        # Logo
        logo_label = toga.Label(
            APP_LOGO,
            style=Pack(text_align="center", font_size=40, padding_bottom=10)
        )
        
        title_label = toga.Label(
            "📖 Quran App",
            style=Pack(text_align="center", font_size=24, font_weight="bold", padding_bottom=20)
        )
        
        # Connection status
        self.connection_status = toga.Label(
            f"🌐 Connected to: {BASE_URL}",
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
            style=Pack(padding=15, background_color=THEME_COLORS["primary"], color="white", padding_bottom=10)
        )
        
        register_student_btn = toga.Button(
            "🎓 Register Student",
            on_press=self.go_to_register_student,
            style=Pack(padding=15, background_color=THEME_COLORS["secondary"], color="white", padding_bottom=10)
        )
        
        register_teacher_btn = toga.Button(
            "👨‍🏫 Register Teacher",
            on_press=self.go_to_register_teacher,
            style=Pack(padding=15, background_color=THEME_COLORS["accent"], color="white")
        )
        
        test_btn = toga.Button(
            "📡 Test Connection",
            on_press=self.test_connection,
            style=Pack(padding=10, background_color=THEME_COLORS["info"], color="white", padding_top=20)
        )
        
        main_box.add(logo_label)
        main_box.add(title_label)
        main_box.add(self.connection_status)
        main_box.add(self.username_input)
        main_box.add(self.password_input)
        main_box.add(login_btn)
        main_box.add(register_student_btn)
        main_box.add(register_teacher_btn)
        main_box.add(test_btn)
        
        self.main_window.content = main_box
    
    def show_dashboard_screen(self):
        self.current_screen = "dashboard"
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        
        title_label = toga.Label(
            f"🎉 Welcome, {self.user['full_name']}!",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        role_label = toga.Label(
            f"Role: {self.user['role']}",
            style=Pack(text_align="center", font_size=14, padding_bottom=30, color=THEME_COLORS["info"])
        )
        
        # Main menu
        menu_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        menu_items = [
            ("📖 Quran", self.show_quran, THEME_COLORS["primary"]),
            ("🎓 My Classes", self.show_my_classes, THEME_COLORS["secondary"]),
            ("📚 Create Class", self.show_create_class, THEME_COLORS["accent"]),
            ("📊 Progress", self.show_progress, THEME_COLORS["info"]),
            ("💬 Chat", self.show_chat, THEME_COLORS["warning"]),
            ("👤 Profile", self.show_profile, THEME_COLORS["success"]),
            ("💰 Payment", self.show_payment, THEME_COLORS["secondary"]),
            ("🚪 Logout", self.logout, THEME_COLORS["danger"])
        ]
        
        for text, handler, color in menu_items:
            if self.user["role"] == "student" and text == "📚 Create Class":
                continue
            if self.user["role"] != "teacher" and text == "📚 Create Class":
                continue
            
            btn = toga.Button(
                text,
                on_press=handler,
                style=Pack(padding=15, background_color=color, color="white", padding_bottom=8)
            )
            menu_box.add(btn)
        
        main_box.add(title_label)
        main_box.add(role_label)
        main_box.add(menu_box)
        
        self.main_window.content = main_box
    
    def show_register_student_screen(self):
        self.current_screen = "register_student"
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        
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
        
        self.student_grade = toga.Selection(
            items=["Beginner", "Intermediate", "Advanced", "Expert"],
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        register_btn = toga.Button(
            "✅ Register",
            on_press=self.register_student_handler,
            style=Pack(padding=15, background_color=THEME_COLORS["success"], color="white", padding_bottom=10)
        )
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_login_screen,
            style=Pack(padding=15, background_color=THEME_COLORS["danger"], color="white")
        )
        
        main_box.add(title_label)
        main_box.add(self.student_username)
        main_box.add(self.student_password)
        main_box.add(self.student_email)
        main_box.add(self.student_fullname)
        main_box.add(self.student_grade)
        main_box.add(register_btn)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def show_register_teacher_screen(self):
        self.current_screen = "register_teacher"
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        
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
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.teacher_specialty = toga.Selection(
            items=["Tajweed", "Recitation", "Tafsir", "Fiqh", "Arabic", "Islamic Studies"],
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        register_btn = toga.Button(
            "✅ Register",
            on_press=self.register_teacher_handler,
            style=Pack(padding=15, background_color=THEME_COLORS["success"], color="white", padding_bottom=10)
        )
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_login_screen,
            style=Pack(padding=15, background_color=THEME_COLORS["danger"], color="white")
        )
        
        main_box.add(title_label)
        main_box.add(self.teacher_username)
        main_box.add(self.teacher_password)
        main_box.add(self.teacher_email)
        main_box.add(self.teacher_fullname)
        main_box.add(self.teacher_specialty)
        main_box.add(register_btn)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def show_quran(self, widget=None):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        
        title_label = toga.Label(
            "📖 Holy Quran",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # Sample surahs list
        surahs = [
            {"id": 1, "name": "Al-Fatiha", "verses": 7},
            {"id": 2, "name": "Al-Baqara", "verses": 286},
            {"id": 3, "name": "Al-Imran", "verses": 200},
            {"id": 4, "name": "An-Nisa", "verses": 176},
            {"id": 5, "name": "Al-Ma'ida", "verses": 120}
        ]
        
        scroll_box = toga.ScrollContainer(style=Pack(flex=1))
        surahs_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        for surah in surahs:
            surah_btn = toga.Button(
                f"{surah['id']}. {surah['name']} ({surah['verses']} verses)",
                on_press=lambda w, s=surah: self.show_surah(s["id"]),
                style=Pack(padding=12, background_color=THEME_COLORS["primary"], color="white", padding_bottom=8)
            )
            surahs_box.add(surah_btn)
        
        scroll_box.content = surahs_box
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_dashboard_screen,
            style=Pack(padding=15, background_color=THEME_COLORS["danger"], color="white", padding_top=20)
        )
        
        main_box.add(title_label)
        main_box.add(scroll_box)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def show_surah(self, surah_id):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        
        title_label = toga.Label(
            f"📖 Surah {surah_id}",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # Sample content
        content_label = toga.Label(
            "Surah content will be displayed here...\n\n"
            "Bismillahir Rahmanir Rahim\n"
            "Alhamdu lillahi rabbil 'alamin\n"
            "Ar-Rahmanir Rahim\n"
            "Maliki yawmid din\n"
            "Iyyaka na'budu wa iyyaka nasta'in\n"
            "Ihdinas siratal mustaqim\n"
            "Siratal lazina an'amta 'alayhim ghayril maghdubi 'alayhim walad dalin",
            style=Pack(padding=10, text_align="left", line_height=1.5)
        )
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_quran,
            style=Pack(padding=15, background_color=THEME_COLORS["danger"], color="white", padding_top=20)
        )
        
        main_box.add(title_label)
        main_box.add(content_label)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def show_my_classes(self, widget=None):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        
        title_label = toga.Label(
            "🎓 My Classes",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # Sample classes
        classes = [
            {"id": 1, "title": "Basic Tajweed", "teacher": "Teacher Ahmed", "time": "Sat & Wed 18-20"},
            {"id": 2, "title": "Quran Recitation", "teacher": "Teacher Mohammad", "time": "Sun & Thu 17-19"},
            {"id": 3, "title": "Quran Tafsir", "teacher": "Teacher Reza", "time": "Mon & Fri 16-18"}
        ]
        
        scroll_box = toga.ScrollContainer(style=Pack(flex=1))
        classes_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        for cls in classes:
            class_card = toga.Box(style=Pack(direction=COLUMN, padding=15, background_color="#f5f5f5", padding_bottom=10))
            
            title = toga.Label(
                cls["title"],
                style=Pack(font_size=16, font_weight="bold", padding_bottom=5)
            )
            
            teacher = toga.Label(
                f"👨‍🏫 {cls['teacher']}",
                style=Pack(font_size=14, padding_bottom=3)
            )
            
            time = toga.Label(
                f"⏰ {cls['time']}",
                style=Pack(font_size=12, color="gray")
            )
            
            join_btn = toga.Button(
                "🎧 Join Class",
                on_press=lambda w, c=cls: self.join_class(c["id"]),
                style=Pack(padding=10, background_color=THEME_COLORS["success"], color="white", padding_top=10)
            )
            
            class_card.add(title)
            class_card.add(teacher)
            class_card.add(time)
            class_card.add(join_btn)
            classes_box.add(class_card)
        
        scroll_box.content = classes_box
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_dashboard_screen,
            style=Pack(padding=15, background_color=THEME_COLORS["danger"], color="white", padding_top=20)
        )
        
        main_box.add(title_label)
        main_box.add(scroll_box)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def show_create_class(self, widget=None):
        if self.user["role"] != "teacher":
            self.show_error("Error", "Only teachers can create classes")
            return
        
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        
        title_label = toga.Label(
            "📚 Create New Class",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        self.class_title = toga.TextInput(
            placeholder="Class Title *",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.class_description = toga.MultilineTextInput(
            placeholder="Class Description",
            style=Pack(padding=10, flex=1, height=100, padding_bottom=10)
        )
        
        self.class_type = toga.Selection(
            items=["Tajweed", "Recitation", "Tafsir", "Fiqh", "Arabic", "Islamic Studies"],
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.class_level = toga.Selection(
            items=["Beginner", "Intermediate", "Advanced"],
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.class_price = toga.NumberInput(
            min_value=0,
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        create_btn = toga.Button(
            "✅ Create Class",
            on_press=self.create_class_handler,
            style=Pack(padding=15, background_color=THEME_COLORS["success"], color="white", padding_bottom=10)
        )
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_dashboard_screen,
            style=Pack(padding=15, background_color=THEME_COLORS["danger"], color="white")
        )
        
        main_box.add(title_label)
        main_box.add(self.class_title)
        main_box.add(self.class_description)
        main_box.add(self.class_type)
        main_box.add(self.class_level)
        main_box.add(toga.Label("💰 Class Price (USDT):", style=Pack(padding_bottom=5)))
        main_box.add(self.class_price)
        main_box.add(create_btn)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def show_chat(self, widget=None):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        
        title_label = toga.Label(
            "💬 Class Chat",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # Sample chat rooms
        classes = [
            {"id": 1, "name": "Basic Tajweed"},
            {"id": 2, "name": "Quran Recitation"},
            {"id": 3, "name": "Quran Tafsir"}
        ]
        
        scroll_box = toga.ScrollContainer(style=Pack(flex=1))
        chat_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        for cls in classes:
            chat_btn = toga.Button(
                f"💬 {cls['name']}",
                on_press=lambda w, c=cls: self.open_chat_room(c["id"]),
                style=Pack(padding=12, background_color=THEME_COLORS["info"], color="white", padding_bottom=8)
            )
            chat_box.add(chat_btn)
        
        scroll_box.content = chat_box
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_dashboard_screen,
            style=Pack(padding=15, background_color=THEME_COLORS["danger"], color="white", padding_top=20)
        )
        
        main_box.add(title_label)
        main_box.add(scroll_box)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def show_progress(self, widget=None):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        
        title_label = toga.Label(
            "📊 Learning Progress",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # Sample progress data
        progress_data = [
            {"subject": "Tajweed", "progress": 75, "grade": "A"},
            {"subject": "Recitation", "progress": 60, "grade": "B"},
            {"subject": "Tafsir", "progress": 85, "grade": "A+"},
            {"subject": "Fiqh", "progress": 45, "grade": "C"}
        ]
        
        scroll_box = toga.ScrollContainer(style=Pack(flex=1))
        progress_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        for data in progress_data:
            progress_card = toga.Box(style=Pack(direction=COLUMN, padding=15, background_color="#f5f5f5", padding_bottom=10))
            
            subject = toga.Label(
                data["subject"],
                style=Pack(font_size=16, font_weight="bold", padding_bottom=5)
            )
            
            progress = toga.Label(
                f"📈 Progress: {data['progress']}%",
                style=Pack(font_size=14, padding_bottom=3)
            )
            
            grade = toga.Label(
                f"🎯 Grade: {data['grade']}",
                style=Pack(font_size=14, color=THEME_COLORS["success"])
            )
            
            progress_card.add(subject)
            progress_card.add(progress)
            progress_card.add(grade)
            progress_box.add(progress_card)
        
        scroll_box.content = progress_box
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_dashboard_screen,
            style=Pack(padding=15, background_color=THEME_COLORS["danger"], color="white", padding_top=20)
        )
        
        main_box.add(title_label)
        main_box.add(scroll_box)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def show_profile(self, widget=None):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        
        title_label = toga.Label(
            "👤 My Profile",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # User information
        profile_box = toga.Box(style=Pack(direction=COLUMN, padding=20, background_color="#f5f5f5"))
        
        info_items = [
            ("👤 Full Name", self.user["full_name"]),
            ("📧 Email", self.user["email"] or "Not set"),
            ("🎯 Role", self.user["role"]),
            ("📊 Level", self.user["grade"] or "Not set"),
            ("🏆 Specialty", self.user["specialty"] or "Not set")
        ]
        
        for icon, value in info_items:
            row = toga.Box(style=Pack(direction=ROW, padding_bottom=10))
            label = toga.Label(
                f"{icon} {value}",
                style=Pack(flex=1, font_size=14)
            )
            row.add(label)
            profile_box.add(row)
        
        edit_btn = toga.Button(
            "✏️ Edit Profile",
            on_press=self.edit_profile,
            style=Pack(padding=15, background_color=THEME_COLORS["warning"], color="white", padding_top=20)
        )
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_dashboard_screen,
            style=Pack(padding=15, background_color=THEME_COLORS["danger"], color="white", padding_top=10)
        )
        
        main_box.add(title_label)
        main_box.add(profile_box)
        main_box.add(edit_btn)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    def show_payment(self, widget=None):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, flex=1))
        
        title_label = toga.Label(
            "💰 Payment & Purchase",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        # Sample classes for purchase
        classes = [
            {"id": 1, "title": "Basic Tajweed", "price": 10.0},
            {"id": 2, "title": "Quran Recitation", "price": 15.0},
            {"id": 3, "title": "Quran Tafsir", "price": 20.0}
        ]
        
        scroll_box = toga.ScrollContainer(style=Pack(flex=1))
        payment_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        for cls in classes:
            payment_card = toga.Box(style=Pack(direction=COLUMN, padding=15, background_color="#f5f5f5", padding_bottom=10))
            
            title = toga.Label(
                cls["title"],
                style=Pack(font_size=16, font_weight="bold", padding_bottom=5)
            )
            
            price = toga.Label(
                f"💰 Price: {cls['price']} USDT",
                style=Pack(font_size=14, padding_bottom=10)
            )
            
            buy_btn = toga.Button(
                "💳 Buy Class",
                on_press=lambda w, c=cls: self.make_payment(c["id"], c["price"]),
                style=Pack(padding=10, background_color=THEME_COLORS["success"], color="white")
            )
            
            payment_card.add(title)
            payment_card.add(price)
            payment_card.add(buy_btn)
            payment_box.add(payment_card)
        
        scroll_box.content = payment_box
        
        back_btn = toga.Button(
            "↩️ Back",
            on_press=self.show_dashboard_screen,
            style=Pack(padding=15, background_color=THEME_COLORS["danger"], color="white", padding_top=20)
        )
        
        main_box.add(title_label)
        main_box.add(scroll_box)
        main_box.add(back_btn)
        
        self.main_window.content = main_box
    
    # -------------------- Handler Methods --------------------
    
    def login_handler(self, widget):
        asyncio.create_task(self.login())
    
    def register_student_handler(self, widget):
        asyncio.create_task(self.register_student())
    
    def register_teacher_handler(self, widget):
        asyncio.create_task(self.register_teacher())
    
    def create_class_handler(self, widget):
        asyncio.create_task(self.create_class())
    
    def test_connection(self, widget):
        asyncio.create_task(self.test_server_connection())
    
    async def login(self):
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        
        if not username or not password:
            self.show_error("Error", "Please enter username and password")
            return
        
        try:
            payload = {"username": username, "password": password}
            response = requests.post(f"{BASE_URL}/login", json=payload, verify=False, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                self.token = response_data["access_token"]
                self.user = await self.get_current_user()
                self.show_info("Success", "Login successful!")
                self.show_dashboard_screen()
            else:
                self.show_error("Error", "Invalid username or password")
                
        except Exception as e:
            self.show_error("Error", f"Server connection error: {str(e)}")
    
    async def register_student(self):
        username = self.student_username.value.strip()
        password = self.student_password.value.strip()
        email = self.student_email.value.strip()
        fullname = self.student_fullname.value.strip()
        grade = self.student_grade.value
        
        if not all([username, password, fullname]):
            self.show_error("Error", "Please fill all required fields")
            return
        
        try:
            payload = {
                "username": username,
                "password": password,
                "full_name": fullname,
                "email": email,
                "grade": grade
            }
            
            response = requests.post(f"{BASE_URL}/register-student", json=payload, verify=False, timeout=30)
            
            if response.status_code == 200:
                self.show_info("Success", "Student registration successful!")
                self.show_login_screen()
            else:
                error_msg = response.json().get("detail", "Registration failed")
                self.show_error("Error", error_msg)
                
        except Exception as e:
            self.show_error("Error", f"Server connection error: {str(e)}")
    
    async def register_teacher(self):
        username = self.teacher_username.value.strip()
        password = self.teacher_password.value.strip()
        email = self.teacher_email.value.strip()
        fullname = self.teacher_fullname.value.strip()
        specialty = self.teacher_specialty.value
        
        if not all([username, password, fullname]):
            self.show_error("Error", "Please fill all required fields")
            return
        
        try:
            payload = {
                "username": username,
                "password": password,
                "full_name": fullname,
                "email": email,
                "specialty": specialty
            }
            
            response = requests.post(f"{BASE_URL}/register-teacher", json=payload, verify=False, timeout=30)
            
            if response.status_code == 200:
                self.show_info("Success", "Teacher registration successful! Waiting for admin approval.")
                self.show_login_screen()
            else:
                error_msg = response.json().get("detail", "Registration failed")
                self.show_error("Error", error_msg)
                
        except Exception as e:
            self.show_error("Error", f"Server connection error: {str(e)}")
    
    async def create_class(self):
        if not self.user or self.user["role"] != "teacher":
            self.show_error("Error", "Only teachers can create classes")
            return
        
        title = self.class_title.value.strip()
        description = self.class_description.value.strip()
        class_type = self.class_type.value
        level = self.class_level.value
        price = float(self.class_price.value or 0)
        
        if not title:
            self.show_error("Error", "Please enter class title")
            return
        
        try:
            payload = {
                "title": title,
                "description": description,
                "class_type": class_type,
                "level": level,
                "price": price
            }
            
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(f"{BASE_URL}/classes", json=payload, headers=headers, verify=False, timeout=30)
            
            if response.status_code == 200:
                self.show_info("Success", "Class created successfully!")
                self.show_dashboard_screen()
            else:
                error_msg = response.json().get("detail", "Class creation failed")
                self.show_error("Error", error_msg)
                
        except Exception as e:
            self.show_error("Error", f"Server connection error: {str(e)}")
    
    async def test_server_connection(self):
        try:
            response = requests.get(f"{BASE_URL}/", verify=False, timeout=10)
            if response.status_code == 200:
                self.show_info("Connection Successful", "Server is responding correctly!")
            else:
                self.show_error("Error", f"Server responded with error: {response.status_code}")
        except Exception as e:
            self.show_error("Error", f"Cannot connect to server: {str(e)}")
    
    async def get_current_user(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/users/me", headers=headers, verify=False, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except:
            return None
    
    def join_class(self, class_id):
        self.show_info("Join Class", f"Connecting to class {class_id}...")
    
    def open_chat_room(self, room_id):
        self.show_info("Chat", f"Opening chat room {room_id}...")
    
    def edit_profile(self, widget):
        self.show_info("Edit", "Profile edit screen")
    
    def make_payment(self, class_id, amount):
        self.show_info("Payment", f"Processing payment of {amount} USDT for class {class_id}...")
    
    def logout(self, widget):
        self.token = None
        self.user = None
        self.show_info("Logout", "Successfully logged out!")
        self.show_login_screen()
    
    def show_error(self, title, message):
        async def show_dialog():
            await self.main_window.error_dialog(title, message)
        asyncio.create_task(show_dialog())
    
    def show_info(self, title, message):
        async def show_dialog():
            await self.main_window.info_dialog(title, message)
        asyncio.create_task(show_dialog())
    
    def go_to_register_student(self, widget):
        self.show_register_student_screen()
    
    def go_to_register_teacher(self, widget):
        self.show_register_teacher_screen()

def main():
    return QuranApp()

if __name__ == "__main__":
    print("🚀 Starting Quran App...")
    app = main()
    app.main_loop()