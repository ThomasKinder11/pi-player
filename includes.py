from player import *
from screensaver import *
import os
import logging
import json

#Just make sure its not causing error redefininf build-in
defined = True

#Color definition
colors = {
    'gray': (0.4,0.4,0.4,1),
    'darkgray': (0.2,0.2,0.2,1),
    'darkestgray': (0.1,0.1,0.1,1),
    'red': (0.5,0.0,0.0,0.8),
    'lightred': (0.8,0.2,0.2,0.3),
    'black' : (0, 0, 0, 1),
    'blue' : (0.5, 0.5, 1, 1),
    'lightblue' : (0, 0, 0.5, 1),
    'orange' : (1,0.5,0.2,1),
}

styles = {
    'defaultEnaColor': colors['blue'],
    'defaultBg': colors['black'],
    'enaColor0': colors['blue'],
    'enaColor1': colors['orange'],
    'warning': colors['lightred'],
    'defaultFiller': colors['lightblue'],
    'itemColor0': colors['darkgray'],
    'itemColor1': colors['darkestgray'],
    'volumeIndicatorBG': colors['gray'],
    'volumeIndicatorColor': colors['blue'],
}

#Media player instance we can use in all modules
player = Player()

#configuration file
syspath = os.path.dirname(os.path.realpath(__file__))
cfgPath = os.path.join(syspath,'config.json')
config = None
with open(cfgPath) as config_file:
    config = json.load(config_file)

logging.error(config)

def writeJson(path, dict):
        f = open(path, "w")
        f.write(json.dumps(dict, sort_keys=True, indent=4))
        f.close()

def writeConfig():
    writeJson(cfgPath, config)

#Global instance of screen saver
screenSaver = None #will be initialized by main-menu

#Generic database, bsically a json file which we read and write
dbPath = os.path.join(syspath, "resources", "database.json")
db = None
try:
    with open(dbPath) as dbFile:
        db = json.load(dbFile)
except:
    f = open(dbPath, "w")
    f.write('''{
                "runtime":0
                }''')
    f.close()

    with open(dbPath) as dbFile:
        db = json.load(dbFile)


def writeDb():
    writeJson(dbPath, db)
