import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import requests


class QuranApp(toga.App):
    def startup(self):
        # ================== فیلدهای ورود ==================
        self.username_input = toga.TextInput(placeholder="Username")
        self.password_input = toga.PasswordInput(placeholder="Password")
        self.login_button = toga.Button("Login", on_press=self.login)
        self.message_label = toga.Label("")

        # ================== چیدمان ==================
        box = toga.Box(
            children=[
                self.username_input,
                self.password_input,
                self.login_button,
                self.message_label,
            ],
            style=Pack(direction=COLUMN, padding=10),
        )

        self.main_window = toga.MainWindow(title="Quran Learning App")
        self.main_window.content = box
        self.main_window.show()

    def login(self, widget):
        username = self.username_input.value
        password = self.password_input.value

        try:
            response = requests.post(
                "http://127.0.0.1:8000/login", json={"username": username, "password": password}
            )
            if response.status_code == 200:
                self.message_label.text = "Login Successful!"
            else:
                self.message_label.text = f"Error: {response.json()['detail']}"
        except Exception as e:
            self.message_label.text = f"Connection error: {e}"


def main():
    return QuranApp("Quran Learning App", "org.example.quran")


if __name__ == "__main__":
    app = main()
    app.main_loop()
