import os
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '0'
os.environ['KIVY_NO_FILELOG'] = '0'
os.environ['KIVY_WINDOW'] = 'sdl2'

import requests
import json
import ssl
import urllib3
from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'resizable', '0')

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock

# غیرفعال کردن هشدارهای SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# URL پایه API
BASE_URL = "https://quran-app-kw38.onrender.com"

Builder.load_string('''
<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 20
        MDLabel:
            text: "Quran App Login"
            halign: "center"
            font_style: "H4"
        MDTextField:
            id: username
            hint_text: "Username"
            size_hint: (1, None)
            height: 50
        MDTextField:
            id: password
            hint_text: "Password"
            password: True
            size_hint: (1, None)
            height: 50
        MDRaisedButton:
            text: "Login"
            size_hint: (1, None)
            height: 50
            on_press: root.login(self)
        MDRaisedButton:
            text: "Register Student"
            size_hint: (1, None)
            height: 50
            on_press: root.go_to_register_student()
        MDRaisedButton:
            text: "Register Teacher"
            size_hint: (1, None)
            height: 50
            on_press: root.go_to_register_teacher()
''')

class LoginScreen(Screen):
    def login(self, instance):
        username = self.ids.username.text
        password = self.ids.password.text
        
        print(f"🔐 Attempting login with username: {username}")
        
        if not username or not password:
            self.show_dialog("Error", "Please enter username and password")
            return
        
        try:
            payload = {"username": username, "password": password}
            print(f"📤 Sending payload: {payload}")
            
            response = requests.post(f"{BASE_URL}/login", json=payload, verify=False, timeout=10)
            
            print(f"📥 Response status code: {response.status_code}")
            print(f"📥 Response content: {response.text}")
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                self.manager.token = token
                self.manager.username = username
                print(f"✅ Login successful! Token: {token}")
                self.show_dialog("Success", "Login successful! Going to dashboard...")
                Clock.schedule_once(lambda dt: self.go_to_dashboard(), 1.0)
            else:
                error_msg = response.json().get('detail', 'Unknown error')
                print(f"❌ Login failed: {error_msg}")
                self.show_dialog("Error", f"Login failed: {error_msg}")
                
        except Exception as e:
            print(f"💥 Exception during login: {str(e)}")
            self.show_dialog("Error", f"Connection error: {str(e)}")
    
    def go_to_dashboard(self):
        print("🔄 Switching to dashboard screen")
        self.manager.current = "dashboard"
    
    def go_to_register_student(self):
        self.manager.current = "register_student"
    
    def go_to_register_teacher(self):
        self.manager.current = "register_teacher"
    
    def show_dialog(self, title, text):
        dialog = MDDialog(title=title, text=text, size_hint=(0.8, 0.4))
        dialog.open()

class DashboardScreen(Screen):
    def on_enter(self):
        if hasattr(self.manager, 'username'):
            print(f"📊 Dashboard opened for user: {self.manager.username}")
    
    def logout(self):
        self.manager.token = None
        self.manager.username = None
        self.manager.current = "login"

class RegisterStudentScreen(Screen):
    pass

class RegisterTeacherScreen(Screen):
    pass

class QuranApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(RegisterStudentScreen(name="register_student"))
        sm.add_widget(RegisterTeacherScreen(name="register_teacher"))
        return sm

if __name__ == "__main__":
    print("🚀 Starting Quran App with Python 3.13...")
    QuranApp().run()
