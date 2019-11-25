'''This is the main loop of the IshaPi player application'''
import logging
from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from menu_main import IshaGui

Logger.setLevel(logging.DEBUG) #TODO: for debuging Pi App should be able to change this

class Main(App):
    '''This is the main class for the IshaPi Player'''
    def build(self):

        return IshaGui()

def run():
    #Window.size = (100, 100)
    from kivy.config import Config
    Config.set('graphics', 'left', '0')
    Config.set('graphics', 'top', '0')


    Main().run()

#if __name__ == "__main__":
#    run()

