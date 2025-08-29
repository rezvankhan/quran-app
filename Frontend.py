from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
import requests
from kivy.clock import Clock
import threading
from functools import partial

# ==============================
# Online server address
BASE_URL = "https://quran-app-kw38.onrender.com"
# ==============================

KV = """
ScreenManager:
    LoginScreen:
    RegisterScreen:
    DashboardScreen:

<LoginScreen>:
    name: "login"
    MDFloatLayout:
        MDLabel:
            text: "Login System"
            halign: "center"
            font_style: "H4"
            pos_hint: {"center_x": 0.5, "center_y": 0.8}
            
        MDTextField:
            id: username
            hint_text: "Username"
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.6}
            mode: "rectangle"
            
        MDTextField:
            id: password
            hint_text: "Password"
            password: True
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            mode: "rectangle"
            
        MDRaisedButton:
            text: "Login"
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5, 'center_y': 0.4}
            on_release: app.login()
            
        MDRaisedButton:
            text: "Register"
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5, 'center_y': 0.3}
            on_release: app.root.current = 'register'

<RegisterScreen>:
    name: "register"
    MDFloatLayout:
        MDLabel:
            text: "User Registration"
            halign: "center"
            font_style: "H4"
            pos_hint: {"center_x": 0.5, "center_y": 0.8}
            
        MDTextField:
            id: reg_username
            hint_text: "Username"
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.6}
            mode: "rectangle"
            
        MDTextField:
            id: reg_password
            hint_text: "Password"
            password: True
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            mode: "rectangle"
            
        MDRaisedButton:
            text: "Complete Registration"
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5, 'center_y': 0.4}
            on_release: app.register()
            
        MDRaisedButton:
            text: "Back to Login"
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5, 'center_y': 0.3}
            on_release: app.root.current = 'login'

<DashboardScreen>:
    name: "dashboard"
    MDFloatLayout:
        MDLabel:
            id: welcome_label
            text: "Welcome!"
            halign: "center"
            font_style: "H4"
            pos_hint: {"center_x": 0.5, "center_y": 0.7}
            
        MDLabel:
            id: user_info
            text: ""
            halign: "center"
            font_style: "Subtitle1"
            pos_hint: {"center_x": 0.5, "center_y": 0.6}
            
        MDRaisedButton:
            text: "Logout"
            size_hint_x: 0.4
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            on_release: app.logout()
            
        MDRaisedButton:
            text: "Refresh"
            size_hint_x: 0.4
            pos_hint: {"center_x": 0.5, "center_y": 0.3}
            on_release: app.refresh_user_info()
"""

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class DashboardScreen(Screen):
    pass

class QDBApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self.sm = Builder.load_string(KV)
        self.user_token = None
        self.username = None
        return self.sm

    def show_toast(self, message):
        Clock.schedule_once(lambda dt: toast(message), 0)

    def show_error_message(self, error_message, dt):
        self.show_toast(f"Error: {error_message}")

    def login(self):
        screen = self.sm.get_screen('login')
        username = screen.ids.username.text.strip()
        password = screen.ids.password.text.strip()
        
        if not username or not password:
            self.show_toast("Please enter username and password")
            return

        def login_thread():
            try:
                print(f"Connecting to: {BASE_URL}/login")
                response = requests.post(
                    f"{BASE_URL}/login",
                    json={"username": username, "password": password},
                    timeout=15
                )
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 200:
                    token = response.json().get("access_token")
                    Clock.schedule_once(lambda dt: self.login_success(username, token))
                else:
                    error_msg = response.json().get("detail", "Login error")
                    Clock.schedule_once(partial(self.show_error_message, error_msg), 0)
                    
            except requests.exceptions.RequestException as e:
                Clock.schedule_once(partial(self.show_error_message, f"Connection error: {str(e)}"), 0)

        threading.Thread(target=login_thread, daemon=True).start()

    def login_success(self, username, token):
        self.show_toast("Login successful")
        self.username = username
        self.user_token = token
        dashboard = self.sm.get_screen('dashboard')
        dashboard.ids.welcome_label.text = f"Welcome, {username}!"
        dashboard.ids.user_info.text = f"Token: {token[:20]}..." if token else "No token"
        self.sm.current = 'dashboard'

    def register(self):
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
                print(f"Connecting to: {BASE_URL}/register")
                response = requests.post(
                    f"{BASE_URL}/register",
                    json={"username": username, "password": password},
                    timeout=15
                )
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.register_success())
                else:
                    error_msg = response.json().get("detail", "Registration error")
                    Clock.schedule_once(partial(self.show_error_message, error_msg), 0)
                    
            except requests.exceptions.RequestException as e:
                Clock.schedule_once(partial(self.show_error_message, f"Connection error: {str(e)}"), 0)

        threading.Thread(target=register_thread, daemon=True).start()

    def register_success(self):
        self.show_toast("Registration successful")
        screen = self.sm.get_screen('register')
        screen.ids.reg_username.text = ""
        screen.ids.reg_password.text = ""
        self.sm.current = 'login'

    def logout(self):
        self.sm.current = 'login'
        self.user_token = None
        self.username = None
        self.show_toast("Logged out successfully")

    def refresh_user_info(self):
        if self.username and self.user_token:
            dashboard = self.sm.get_screen('dashboard')
            dashboard.ids.user_info.text = f"User: {self.username}\nToken: {self.user_token[:20]}..."
            self.show_toast("Information refreshed")

if __name__ == "__main__":
    QDBApp().run()
