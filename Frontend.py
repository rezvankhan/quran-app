from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
import requests
from kivy.clock import Clock
import threading

# ==============================
# برای تست روی شبکه محلی - در production تغییر دهید
BASE_URL = "http://192.168.1.100:8080"  # IP کامپیوتر خودتان
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
            text: "سیستم ورود"
            halign: "center"
            font_style: "H4"
            pos_hint: {"center_x": 0.5, "center_y": 0.8}
            
        MDTextField:
            id: username
            hint_text: "نام کاربری"
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.6}
            mode: "rectangle"
            
        MDTextField:
            id: password
            hint_text: "رمز عبور"
            password: True
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            mode: "rectangle"
            
        MDRaisedButton:
            text: "ورود"
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5, 'center_y': 0.4}
            on_release: app.login()
            
        MDRaisedButton:
            text: "ثبت نام"
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5, 'center_y': 0.3}
            on_release: app.root.current = 'register'

<RegisterScreen>:
    name: "register"
    MDFloatLayout:
        MDLabel:
            text: "ثبت نام کاربر"
            halign: "center"
            font_style: "H4"
            pos_hint: {"center_x": 0.5, "center_y": 0.8}
            
        MDTextField:
            id: reg_username
            hint_text: "نام کاربری"
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.6}
            mode: "rectangle"
            
        MDTextField:
            id: reg_password
            hint_text: "رمز عبور"
            password: True
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            mode: "rectangle"
            
        MDRaisedButton:
            text: "تکمیل ثبت نام"
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5, 'center_y': 0.4}
            on_release: app.register()
            
        MDRaisedButton:
            text: "بازگشت"
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5, 'center_y': 0.3}
            on_release: app.root.current = 'login'

<DashboardScreen>:
    name: "dashboard"
    MDFloatLayout:
        MDLabel:
            id: welcome_label
            text: "خوش آمدید!"
            halign: "center"
            font_style: "H4"
            pos_hint: {"center_x": 0.5, "center_y": 0.6}
            
        MDRaisedButton:
            text: "خروج"
            size_hint_x: 0.4
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            on_release: app.logout()
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
        return self.sm

    def show_toast(self, message):
        Clock.schedule_once(lambda dt: toast(message), 0)

    def login(self):
        screen = self.sm.get_screen('login')
        username = screen.ids.username.text.strip()
        password = screen.ids.password.text.strip()
        
        if not username or not password:
            self.show_toast("لطفاً نام کاربری و رمز عبور را وارد کنید")
            return

        def login_thread():
            try:
                response = requests.post(
                    f"{BASE_URL}/login",
                    json={"username": username, "password": password},
                    timeout=10
                )
                
                if response.status_code == 200:
                    token = response.json().get("access_token")
                    Clock.schedule_once(lambda dt: self.login_success(username, token))
                else:
                    error_msg = response.json().get("detail", "خطا در ورود")
                    Clock.schedule_once(lambda dt: self.show_toast(f"خطا: {error_msg}"))
                    
            except requests.exceptions.RequestException as e:
                Clock.schedule_once(lambda dt: self.show_toast(f"خطای اتصال: {str(e)}"))

        threading.Thread(target=login_thread, daemon=True).start()

    def login_success(self, username, token):
        self.show_toast("ورود موفقیت‌آمیز بود")
        dashboard = self.sm.get_screen('dashboard')
        dashboard.ids.welcome_label.text = f"خوش آمدید، {username}!"
        self.sm.current = 'dashboard'
        self.user_token = token

    def register(self):
        screen = self.sm.get_screen('register')
        username = screen.ids.reg_username.text.strip()
        password = screen.ids.reg_password.text.strip()
        
        if not username or not password:
            self.show_toast("لطفاً نام کاربری و رمز عبور را وارد کنید")
            return
        
        if len(password) < 6:
            self.show_toast("رمز عبور باید حداقل 6 کاراکتر باشد")
            return

        def register_thread():
            try:
                response = requests.post(
                    f"{BASE_URL}/register",
                    json={"username": username, "password": password},
                    timeout=10
                )
                
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.register_success())
                else:
                    error_msg = response.json().get("detail", "خطا در ثبت‌نام")
                    Clock.schedule_once(lambda dt: self.show_toast(f"خطا: {error_msg}"))
                    
            except requests.exceptions.RequestException as e:
                Clock.schedule_once(lambda dt: self.show_toast(f"خطای اتصال: {str(e)}"))

        threading.Thread(target=register_thread, daemon=True).start()

    def register_success(self):
        self.show_toast("ثبت‌نام موفقیت‌آمیز بود")
        screen = self.sm.get_screen('register')
        screen.ids.reg_username.text = ""
        screen.ids.reg_password.text = ""
        self.sm.current = 'login'

    def logout(self):
        self.sm.current = 'login'
        self.show_toast("خروج انجام شد")

if __name__ == "__main__":
    QDBApp().run()