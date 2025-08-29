from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
import requests
from kivy.clock import Clock
import threading
from functools import partial

BASE_URL = "https://quran-app-kw38.onrender.com"

KV = """
#:import hex kivy.utils.get_color_from_hex

<BlueLayout@BoxLayout>:
    canvas.before:
        Color:
            rgba: hex('#87CEEB')
        Rectangle:
            pos: self.pos
            size: self.size

ScreenManager:
    LoginScreen:
    RegisterScreen:
    TeacherRegistrationScreen:
    DashboardScreen:

<LoginScreen>:
    name: "login"
    
    BlueLayout:
        orientation: "vertical"
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
            size_hint_x: None
            width: "300dp"
            pos_hint: {"center_x": 0.5}
            mode: "rectangle"
            
        MDTextField:
            id: password
            hint_text: "Password"
            password: True
            size_hint_x: None
            width: "300dp"
            pos_hint: {"center_x": 0.5}
            mode: "rectangle"
            
        MDRaisedButton:
            text: "Login"
            size_hint_x: None
            width: "200dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.login()
            
        MDRaisedButton:
            text: "Register Student"
            size_hint_x: None
            width: "200dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = 'register'
            
        MDRaisedButton:
            text: "Register Teacher"
            size_hint_x: None
            width: "200dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = 'register_teacher'

<RegisterScreen>:
    name: "register"
    
    BlueLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "20dp"
        
        MDLabel:
            text: "Student Registration"
            halign: "center"
            font_style: "H4"
            
        MDTextField:
            id: reg_username
            hint_text: "Username"
            size_hint_x: None
            width: "300dp"
            pos_hint: {"center_x": 0.5}
            
        MDTextField:
            id: reg_password
            hint_text: "Password"
            password: True
            size_hint_x: None
            width: "300dp"
            pos_hint: {"center_x": 0.5}
            
        MDRaisedButton:
            text: "Register"
            size_hint_x: None
            width: "200dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.register_student()
            
        MDRaisedButton:
            text: "Back to Login"
            size_hint_x: None
            width: "200dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = 'login'

<TeacherRegistrationScreen>:
    name: "register_teacher"
    
    BlueLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "20dp"
        
        MDLabel:
            text: "Teacher Registration"
            halign: "center"
            font_style: "H4"
            
        MDTextField:
            id: teacher_username
            hint_text: "Username"
            size_hint_x: None
            width: "300dp"
            pos_hint: {"center_x": 0.5}
            
        MDTextField:
            id: teacher_password
            hint_text: "Password"
            password: True
            size_hint_x: None
            width: "300dp"
            pos_hint: {"center_x": 0.5}
            
        MDRaisedButton:
            text: "Register Teacher"
            size_hint_x: None
            width: "200dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.register_teacher()
            
        MDRaisedButton:
            text: "Back to Login"
            size_hint_x: None
            width: "200dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = 'login'

<DashboardScreen>:
    name: "dashboard"
    
    BlueLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "20dp"
        
        MDLabel:
            id: welcome_label
            text: "Welcome!"
            halign: "center"
            font_style: "H4"
            
        MDLabel:
            id: user_info
            text: ""
            halign: "center"
            font_style: "Subtitle1"
            
        MDRaisedButton:
            text: "Create Class"
            size_hint_x: None
            width: "200dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.show_create_class_dialog()
            
        MDRaisedButton:
            text: "Open Chat"
            size_hint_x: None
            width: "200dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.open_chat()
            
        MDRaisedButton:
            text: "Logout"
            size_hint_x: None
            width: "200dp"
            pos_hint: {"center_x": 0.5}
            on_release: app.logout()
"""

class BlueLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            from kivy.utils import get_color_from_hex
            Color(*get_color_from_hex('#87CEEB'))
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class TeacherRegistrationScreen(Screen):
    pass

class DashboardScreen(Screen):
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

    def login(self):
        screen = self.sm.get_screen('login')
        username = screen.ids.username.text.strip()
        password = screen.ids.password.text.strip()
        
        if not username or not password:
            self.show_toast("Please enter username and password")
            return

        def login_thread():
            try:
                response = requests.post(
                    f"{BASE_URL}/login",
                    json={"username": username, "password": password},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("access_token")
                    if token:
                        Clock.schedule_once(lambda dt: self.login_success(username, token))
                    else:
                        Clock.schedule_once(lambda dt: self.show_error("No token received"))
                else:
                    error_msg = response.json().get("detail", "Login failed")
                    Clock.schedule_once(partial(self.show_error, error_msg), 0)
                    
            except requests.exceptions.RequestException as e:
                Clock.schedule_once(partial(self.show_error, f"Connection error: {str(e)}"), 0)

        threading.Thread(target=login_thread, daemon=True).start()

    def login_success(self, username, token):
        self.show_toast("Login successful")
        self.username = username
        self.user_token = token
        
        def get_user_info():
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    f"{BASE_URL}/users/me",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.user_data = response.json()
                    Clock.schedule_once(lambda dt: self.update_dashboard())
                else:
                    print("Failed to get user info")
                    
            except Exception as e:
                print(f"Error getting user info: {e}")
        
        threading.Thread(target=get_user_info, daemon=True).start()

    def update_dashboard(self):
        dashboard = self.sm.get_screen('dashboard')
        dashboard.ids.welcome_label.text = f"Welcome, {self.username}!"
        
        if self.user_data:
            user_info = (
                f"Role: {self.user_data.get('role', 'N/A')}\n"
                f"Approved: {'Yes' if self.user_data.get('approved') else 'No'}"
            )
            dashboard.ids.user_info.text = user_info
        
        self.sm.current = 'dashboard'

    def register_student(self):
        screen = self.sm.get_screen('register')
        username = screen.ids.reg_username.text.strip()
        password = screen.ids.reg_password.text.strip()
        
        if not username or not password:
            self.show_toast("Please enter username and password")
            return
        
        if len(password) < 6:
            self.show_toast("Password must be at least 6 characters")
            return

        def register_thread():
            try:
                response = requests.post(
                    f"{BASE_URL}/register",
                    json={"username": username, "password": password},
                    timeout=15
                )
                
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.register_success())
                else:
                    error_msg = response.json().get("detail", "Registration failed")
                    Clock.schedule_once(partial(self.show_error, error_msg), 0)
                    
            except requests.exceptions.RequestException as e:
                Clock.schedule_once(partial(self.show_error, f"Connection error: {str(e)}"), 0)

        threading.Thread(target=register_thread, daemon=True).start()

    def register_teacher(self):
        screen = self.sm.get_screen('register_teacher')
        username = screen.ids.teacher_username.text.strip()
        password = screen.ids.teacher_password.text.strip()
        
        if not username or not password:
            self.show_toast("Please enter username and password")
            return
        
        if len(password) < 6:
            self.show_toast("Password must be at least 6 characters")
            return

        def register_thread():
            try:
                response = requests.post(
                    f"{BASE_URL}/register",
                    json={"username": username, "password": password, "role": "teacher"},
                    timeout=15
                )
                
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.register_success())
                else:
                    error_msg = response.json().get("detail", "Registration failed")
                    Clock.schedule_once(partial(self.show_error, error_msg), 0)
                    
            except requests.exceptions.RequestException as e:
                Clock.schedule_once(partial(self.show_error, f"Connection error: {str(e)}"), 0)

        threading.Thread(target=register_thread, daemon=True).start()

    def register_success(self):
        self.show_toast("Registration successful")
        self.sm.current = 'login'

    def logout(self):
        self.sm.current = 'login'
        self.user_token = None
        self.user_data = None
        self.show_toast("Logged out successfully")

    def show_create_class_dialog(self):
        self.show_toast("Class creation feature coming soon!")

    def open_chat(self):
        self.show_toast("Chat feature coming soon!")

if __name__ == "__main__":
    QuranEducationApp().run()
