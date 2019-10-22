from player import *
import logging
import os
from  subprocess import Popen
from kivy.core.window import Window

"""
This is the media player we use for isha pi project.
On Raspberri PI we will be using the openmx player.
On virtual machines and testing on windows we can use mpv player
"""
class Player():
    exec = None
    supportedPlayers = {}
    process = None

    def play(self, path):
        logging.info("Player: start playing file... path = {}".format(path))

        if not os.path.isfile(path):
            logging.error("Player: file not found")


        windowWidthOrig = Window.width# 1440 #Todo: make dynamic
        windowHeightOrig = Window.height #900 #Todo: make dynamic
        windowWidth = windowWidthOrig

        if windowWidthOrig >= 1800:
            windowWidth = 1600

        windowWidth = 1280

        windowHeight = (9 / 16) * windowWidthOrig

        posx = int(int((windowWidthOrig) - (windowWidth)) / 2)
        posy = int((windowHeightOrig - windowHeight) / 2)

        logging.error("Player: start media player...")
        self.process = Popen([self.supportedPlayers[os.name],
                        "--geometry={}+{}+{}".format(windowWidth, posx, posy),
                        "--no-border",
                        "--no-input-default-bindings",
                        path,
                        "--no-input-default-bindings",
                        "--input-ipc-server=C:\\tmp\\socket"

])
#"--really-quiet",
#"--no-osc",

# "--input-ipc-server={}".format(os.path.join(globals.config[os.name]['tmpdir'], "ishapiSocket")


    def __init__(self, **kwargs):
        self.supportedPlayers['nt'] = "mpv.exe"
        self.supportedPlayers['posix'] = "mpv"

        pass
