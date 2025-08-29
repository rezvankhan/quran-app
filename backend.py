# Frontend.py - قسمت‌های مهم

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
            
            print(f"Login Status: {response.status_code}")
            print(f"Login Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                user_data = data.get("user", {})
                if token:
                    Clock.schedule_once(lambda dt: self.login_success(username, token, user_data))
                else:
                    Clock.schedule_once(lambda dt: self.show_error("No token received"))
            else:
                try:
                    error_msg = response.json().get("detail", "Login failed")
                except:
                    error_msg = f"HTTP Error {response.status_code}"
                Clock.schedule_once(lambda dt: self.show_error(error_msg))
                
        except requests.exceptions.RequestException as e:
            Clock.schedule_once(lambda dt: self.show_error(f"Connection error: {str(e)}"))

    threading.Thread(target=login_thread, daemon=True).start()

def login_success(self, username, token, user_data):
    self.show_toast("Login successful")
    self.username = username
    self.user_token = token
    self.user_data = user_data
    self.update_dashboard()

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
                json={"username": username, "password": password, "role": "student"},
                timeout=15
            )
            
            print(f"Register Status: {response.status_code}")
            print(f"Register Response: {response.text}")
            
            if response.status_code == 200:
                Clock.schedule_once(lambda dt: self.register_success())
            else:
                try:
                    error_msg = response.json().get("detail", "Registration failed")
                except:
                    error_msg = f"HTTP Error {response.status_code}"
                Clock.schedule_once(lambda dt: self.show_error(error_msg))
                
        except requests.exceptions.RequestException as e:
            Clock.schedule_once(lambda dt: self.show_error(f"Connection error: {str(e)}"))

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
            
            print(f"Teacher Register Status: {response.status_code}")
            print(f"Teacher Register Response: {response.text}")
            
            if response.status_code == 200:
                Clock.schedule_once(lambda dt: self.register_success())
            else:
                try:
                    error_msg = response.json().get("detail", "Registration failed")
                except:
                    error_msg = f"HTTP Error {response.status_code}"
                Clock.schedule_once(lambda dt: self.show_error(error_msg))
                
        except requests.exceptions.RequestException as e:
            Clock.schedule_once(lambda dt: self.show_error(f"Connection error: {str(e)}"))

    threading.Thread(target=register_thread, daemon=True).start()
