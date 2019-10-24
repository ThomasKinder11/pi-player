from player import *
from screensaver import *
import os
import logging
import json

#Media player instance we can use in all modules
player = Player()


#configuration file
syspath = os.path.realpath(__file__)
cfgPath = os.path.join(os.path.dirname(syspath),'config.json')
config = None
with open(cfgPath) as config_file:
    config = json.load(config_file)

def writeConfig():
    logging.info("ConfigGLobals: write file ................................ ")
    f = open(cfgPath, "w")
    f.write(json.dumps(config, sort_keys=True, indent=4))
    f.close()

#Global instance of screen saver
screenSaver = None #will be initialized by main-menu
