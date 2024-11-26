from kivy.app import App
from kivy.uix.label import Label
from threading import Thread
import os

def start_flask_server():
    os.system("python server.py")

class FlaskKivyApp(App):
    def build(self):
        # Start Flask server in a separate thread
        Thread(target=start_flask_server, daemon=True).start()
        return Label(text="Flask Server is Running!\nOpen http://<your-device-ip>:5000")

if __name__ == '__main__':
    FlaskKivyApp().run()
