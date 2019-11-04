'''This is the main loop of the IshaPi player application'''
import logging
from kivy.app import App
from kivy.logger import Logger
from menu_main import IshaGui
#Logger.setLevel(logging.WARNING) #TODO: for debuging Pi App should be able to change this

class Main(App):
    '''This is the main class for the IshaPi Player'''
    def build(self):

        return IshaGui()

if __name__ == "__main__":

    Main().run()
