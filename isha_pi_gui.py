from isha_pi_kivy import *
from menu_main import Menu, IshaPiScreens
from kivy.config import Config

from kivy.app import App
from kivy.core.window import Window

class Main(App):
    def build(self):
        tmp = IshaPiScreens()
        tmp.current = "main_menu"
        return tmp

if __name__ == "__main__":
    Main().run()
