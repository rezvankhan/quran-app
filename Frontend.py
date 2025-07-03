from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
import requests

KV = '''
ScreenManager:
    LoginScreen:
    RegisterScreen:

<LoginScreen>:
    name: "login"
    MDTextField:
        id: username_input
        hint_text: "Username"
        pos_hint: {"center_x": 0.5, "center_y": 0.7}
        size_hint_x: 0.8
    MDTextField:
        id: password_input
        hint_text: "Password"
        password: True
        pos_hint: {"center_x": 0.5, "center_y": 0.6}
        size_hint_x: 0.8
    MDRaisedButton:
        text: "Login"
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        on_release: app.login()
    MDFlatButton:
        text: "Register"
        pos_hint: {"center_x": 0.5, "center_y": 0.4}
        on_release: app.change_screen("register")

<RegisterScreen>:
    name: "register"
    MDTextField:
        id: reg_username_input
        hint_text: "Username"
        pos_hint: {"center_x": 0.5, "center_y": 0.7}
        size_hint_x: 0.8
    MDTextField:
        id: reg_password_input
        hint_text: "Password"
        password: True
        pos_hint: {"center_x": 0.5, "center_y": 0.6}
        size_hint_x: 0.8
    MDTextField:
        id: reg_role_input
        hint_text: "Role (student / teacher)"
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        size_hint_x: 0.8
    MDRaisedButton:
        text: "Submit"
        pos_hint: {"center_x": 0.5, "center_y": 0.4}
        on_release: app.register()
    MDFlatButton:
        text: "Back to Login"
        pos_hint: {"center_x": 0.5, "center_y": 0.3}
        on_release: app.change_screen("login")
'''

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class QuranApp(MDApp):
    def build(self):
        self.root = Builder.load_string(KV)
        return self.root

    def change_screen(self, screen_name):
        self.root.current = screen_name

    def login(self):
        username = self.root.get_screen("login").ids.username_input.text
        password = self.root.get_screen("login").ids.password_input.text
        data = {
            "username": username,
            "password": password,
            "role": "student"
        }
        response = requests.post("http://127.0.0.1:8000/login", json=data)
        if response.status_code == 200:
            print("Login successful")
            # Change to another screen here
        else:
            print("Login failed")

    def register(self):
        username = self.root.get_screen("register").ids.reg_username_input.text
        password = self.root.get_screen("register").ids.reg_password_input.text
        role = self.root.get_screen("register").ids.reg_role_input.text
        data = {
            "username": username,
            "password": password,
            "role": role
        }
        response = requests.post("http://127.0.0.1:8000/register", json=data)
        if response.status_code == 200:
            print("Registration successful")
            self.change_screen("login")
        else:
            print("Registration failed")

if __name__ == "__main__":
    QuranApp().run()