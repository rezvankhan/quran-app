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

# غیرفعال کردن هشدارها
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore", category=DeprecationWarning)

# URL پایه API
BASE_URL = "https://quran-app-kw38.onrender.com"

# تم برنامه
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
        
        # لوگو
        logo_label = toga.Label(
            APP_LOGO,
            style=Pack(text_align="center", font_size=40, padding_bottom=10)
        )
        
        title_label = toga.Label(
            "📖 قرآن اپ",
            style=Pack(text_align="center", font_size=24, font_weight="bold", padding_bottom=20)
        )
        
        # وضعیت اتصال
        self.connection_status = toga.Label(
            f"🌐 متصل به: {BASE_URL}",
            style=Pack(text_align="center", font_size=10, color="gray", padding_bottom=20)
        )
        
        self.username_input = toga.TextInput(
            placeholder="نام کاربری",
            style=Pack(padding=12, flex=1, padding_bottom=10)
        )
        
        self.password_input = toga.PasswordInput(
            placeholder="رمز عبور",
            style=Pack(padding=12, flex=1, padding_bottom=20)
        )
        
        login_btn = toga.Button(
            "🔐 ورود به سیستم",
            on_press=self.login_handler,
            style=Pack(padding=15, background_color=THEME_COLORS["primary"], color="white", padding_bottom=10)
        )
        
        register_student_btn = toga.Button(
            "🎓 ثبت نام دانشجو",
            on_press=self.go_to_register_student,
            style=Pack(padding=15, background_color=THEME_COLORS["secondary"], color="white", padding_bottom=10)
        )
        
        register_teacher_btn = toga.Button(
            "👨‍🏫 ثبت نام استاد",
            on_press=self.go_to_register_teacher,
            style=Pack(padding=15, background_color=THEME_COLORS["accent"], color="white")
        )
        
        test_btn = toga.Button(
            "📡 تست اتصال سرور",
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
            f"🎉 خوش آمدید، {self.user['full_name']}!",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        role_label = toga.Label(
            f"نقش: {self.user['role']}",
            style=Pack(text_align="center", font_size=14, padding_bottom=30, color=THEME_COLORS["info"])
        )
        
        # منوی اصلی
        menu_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        menu_items = [
            ("📖 قرآن کریم", self.show_quran, THEME_COLORS["primary"]),
            ("🎓 کلاس‌های من", self.show_my_classes, THEME_COLORS["secondary"]),
            ("📚 ایجاد کلاس", self.show_create_class, THEME_COLORS["accent"]),
            ("📊 پیشرفت تحصیلی", self.show_progress, THEME_COLORS["info"]),
            ("💬 چت کلاسی", self.show_chat, THEME_COLORS["warning"]),
            ("👤 پروفایل من", self.show_profile, THEME_COLORS["success"]),
            ("💰 پرداخت و خرید", self.show_payment, THEME_COLORS["secondary"]),
            ("🚪 خروج از سیستم", self.logout, THEME_COLORS["danger"])
        ]
        
        for text, handler, color in menu_items:
            if self.user["role"] == "student" and text == "📚 ایجاد کلاس":
                continue
            if self.user["role"] != "teacher" and text == "📚 ایجاد کلاس":
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
            "🎓 ثبت نام دانشجو",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        self.student_username = toga.TextInput(
            placeholder="نام کاربری *",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.student_password = toga.PasswordInput(
            placeholder="رمز عبور *",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.student_email = toga.TextInput(
            placeholder="ایمیل",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.student_fullname = toga.TextInput(
            placeholder="نام کامل *",
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        self.student_grade = toga.Selection(
            items=["مقدماتی", "متوسط", "پیشرفته", "تخصصی"],
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        register_btn = toga.Button(
            "✅ ثبت نام",
            on_press=self.register_student_handler,
            style=Pack(padding=15, background_color=THEME_COLORS["success"], color="white", padding_bottom=10)
        )
        
        back_btn = toga.Button(
            "↩️ بازگشت",
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
            "👨‍🏫 ثبت نام استاد",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        self.teacher_username = toga.TextInput(
            placeholder="نام کاربری *",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.teacher_password = toga.PasswordInput(
            placeholder="رمز عبور *",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.teacher_email = toga.TextInput(
            placeholder="ایمیل",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.teacher_fullname = toga.TextInput(
            placeholder="نام کامل *",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.teacher_specialty = toga.Selection(
            items=["تجوید", "قرائت", "تفسیر", "فقه", "عربی", "اسلامیات"],
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        register_btn = toga.Button(
            "✅ ثبت نام",
            on_press=self.register_teacher_handler,
            style=Pack(padding=15, background_color=THEME_COLORS["success"], color="white", padding_bottom=10)
        )
        
        back_btn = toga.Button(
            "↩️ بازگشت",
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
    
    # بقیه متدها بدون تغییر...
    
    def login_handler(self, widget):
        asyncio.create_task(self.login())
    
    def register_student_handler(self, widget):
        asyncio.create_task(self.register_student())
    
    def register_teacher_handler(self, widget):
        asyncio.create_task(self.register_teacher())
    
    def test_connection(self, widget):
        asyncio.create_task(self.test_server_connection())
    
    async def login(self):
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        
        if not username or not password:
            self.show_error("خطا", "لطفا نام کاربری و رمز عبور را وارد کنید")
            return
        
        try:
            payload = {"username": username, "password": password}
            response = requests.post(f"{BASE_URL}/login", json=payload, verify=False, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                self.token = response_data["access_token"]
                self.user = await self.get_current_user()
                self.show_info("موفقیت", "ورود موفقیت‌آمیز بود")
                self.show_dashboard_screen()
            else:
                self.show_error("خطا", "نام کاربری или رمز عبور اشتباه است")
                
        except Exception as e:
            self.show_error("خطا", f"خطا در ارتباط با سرور: {str(e)}")
    
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
    
    def logout(self, widget):
        self.token = None
        self.user = None
        self.show_info("خروج", "با موفقیت از سیستم خارج شدید")
        self.show_login_screen()

def main():
    return QuranApp()

if __name__ == "__main__":
    print("🚀 Starting Quran App...")
    app = main()
    app.main_loop()
