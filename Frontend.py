import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import requests
import ssl
import urllib3
import json
import asyncio

# غیرفعال کردن هشدارهای SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# URL پایه API - ابتدا از localhost تست کنید
BASE_URL = "http://localhost:8000"  # یا آدرس سرور واقعی شما

class QuranApp(toga.App):
    def __init__(self):
        super().__init__('Quran App', 'com.quran.app')
        self.token = None
        self.username = None
    
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400, 500))
        self.show_login_screen()
        self.main_window.show()
    
    def show_login_screen(self):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=40))
        
        title_label = toga.Label(
            "Quran App Login",
            style=Pack(text_align="center", font_size=20, font_weight="bold", padding_bottom=20)
        )
        
        self.username_input = toga.TextInput(
            placeholder="Username",
            style=Pack(padding=10, flex=1, padding_bottom=10)
        )
        
        self.password_input = toga.PasswordInput(
            placeholder="Password",
            style=Pack(padding=10, flex=1, padding_bottom=20)
        )
        
        login_btn = toga.Button(
            "Login",
            on_press=self.login_handler,
            style=Pack(padding=15, background_color="#4CAF50", color="white", padding_bottom=10)
        )
        
        main_box.add(title_label)
        main_box.add(self.username_input)
        main_box.add(self.password_input)
        main_box.add(login_btn)
        
        self.main_window.content = main_box
    
    def login_handler(self, widget):
        asyncio.create_task(self.login())
    
    async def login(self):
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        
        if not username or not password:
            self.show_error("Error", "Please enter username and password")
            return
        
        try:
            # تست اتصال اولیه
            test_response = requests.get(f"{BASE_URL}/", verify=False, timeout=10)
            print(f"Connection test: {test_response.status_code}")
            
            payload = {"username": username, "password": password}
            response = requests.post(f"{BASE_URL}/login", json=payload, verify=False, timeout=30)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    self.show_info("Success", "Login successful!")
                except json.JSONDecodeError:
                    self.show_error("Error", "Invalid server response")
            else:
                self.show_error("Error", f"Server returned {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.show_error("Error", "Cannot connect to server. Please check if server is running.")
        except Exception as e:
            self.show_error("Error", f"Unexpected error: {str(e)}")
    
    def show_error(self, title, message):
        async def show_dialog():
            await self.main_window.error_dialog(title, message)
        asyncio.create_task(show_dialog())
    
    def show_info(self, title, message):
        async def show_dialog():
            await self.main_window.info_dialog(title, message)
        asyncio.create_task(show_dialog())

def main():
    return QuranApp()

if __name__ == "__main__":
    print("Starting Quran App...")
    app = main()
    app.main_loop()
