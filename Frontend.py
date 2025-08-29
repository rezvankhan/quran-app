# frontend.py (کامل شده)
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.toast import toast
import requests
from kivy.clock import Clock
import threading
from functools import partial

BASE_URL = "https://quran-app-kw38.onrender.com"

KV = """
#:import hex kivy.utils.get_color_from_hex

<BlueBackground@BoxLayout>
    canvas.before:
        Color:
            rgba: hex('#87CEEB')
        Rectangle:
            pos: self.pos
            size: self.size

ScreenManager:
    LoginScreen:
    RegisterScreen:
    DashboardScreen:
    TeacherRegistrationScreen:
    ClassManagementScreen:
    ExamScreen:
    ChatScreen:

<LoginScreen>:
    name: "login"
    BlueBackground:
        MDCard:
            size_hint: None, None
            size: "400dp", "500dp"
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            elevation: 10
            padding: "20dp"
            spacing: "20dp"
            
            MDLabel:
                text: "Quran Education System"
                halign: "center"
                font_style: "H4"
                size_hint_y: None
                height: self.texture_size[1]
                
            MDTextField:
                id: username
                hint_text: "Username"
                size_hint_x: 0.8
                pos_hint: {"center_x": 0.5}
                mode: "rectangle"
                
            MDTextField:
                id: password
                hint_text: "Password"
                password: True
                size_hint_x: 0.8
                pos_hint: {"center_x": 0.5}
                mode: "rectangle"
                
            MDRaisedButton:
                text: "Login"
                size_hint_x: 0.6
                pos_hint: {"center_x": 0.5}
                on_release: app.login()
                
            MDRaisedButton:
                text: "Register"
                size_hint_x: 0.6
                pos_hint: {"center_x": 0.5}
                on_release: app.root.current = 'register'
                
            MDRaisedButton:
                text: "Register as Teacher"
                size_hint_x: 0.6
                pos_hint: {"center_x": 0.5}
                on_release: app.root.current = 'register_teacher'

<RegisterScreen>:
    name: "register"
    BlueBackground:
        # Similar to LoginScreen but for student registration

<TeacherRegistrationScreen>:
    name: "register_teacher"
    BlueBackground:
        # Teacher registration form

<DashboardScreen>:
    name: "dashboard"
    BlueBackground:
        # Dashboard with user info and navigation

<ClassManagementScreen>:
    name: "class_management"
    BlueBackground:
        # Class creation and management

<ExamScreen>:
    name: "exam_screen"
    BlueBackground:
        # Exam creation and taking

<ChatScreen>:
    name: "chat_screen"
    BlueBackground:
        # Chat interface
"""

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class TeacherRegistrationScreen(Screen):
    pass

class DashboardScreen(Screen):
    pass

class ClassManagementScreen(Screen):
    pass

class ExamScreen(Screen):
    pass

class ChatScreen(Screen):
    pass

class QuranEducationApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.sm = Builder.load_string(KV)
        self.user_token = None
        self.user_data = None
        return self.sm

    def show_toast(self, message):
        Clock.schedule_once(lambda dt: toast(message), 0)

    def show_error(self, message):
        self.dialog = MDDialog(title="Error", text=message, size_hint=(0.8, 0.3))
        self.dialog.open()

    # تمام متدهای قبلی + متدهای جدید برای مدیریت کلاس‌ها، آزمون‌ها و چت
    
    def register_teacher(self, username, password):
        def register_thread():
            try:
                response = requests.post(
                    f"{BASE_URL}/register-teacher",
                    json={"username": username, "password": password, "role": "teacher"},
                    headers={"Authorization": f"Bearer {self.user_token}"},
                    timeout=15
                )
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.show_toast("Teacher registration submitted for approval"))
                else:
                    error_msg = response.json().get("detail", "Registration failed")
                    Clock.schedule_once(partial(self.show_error, error_msg), 0)
            except Exception as e:
                Clock.schedule_once(partial(self.show_error, f"Connection error: {str(e)}"), 0)
        
        threading.Thread(target=register_thread, daemon=True).start()

    def create_class(self, name, level, schedule_time):
        # متد ایجاد کلاس
        pass

    def create_exam(self, title, description, class_id, duration):
        # متد ایجاد آزمون
        pass

    def send_message(self, message, receiver_id=None, class_id=None):
        # متد ارسال پیام
        pass

if __name__ == "__main__":
    QuranEducationApp().run()
