'''This is the main loop of the IshaPi player application'''
from kivy.app import App
from menu_main import IshaGui


class Main(App):
    '''This is the main class for the IshaPi Player'''
    def build(self):
        return IshaGui()

if __name__ == "__main__":
    Main().run()
