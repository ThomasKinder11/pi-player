from player import *
from screensaver import *
import os
import logging
import json

#Media player instance we can use in all modules
player = Player()


#configuration file
syspath = os.path.dirname(os.path.realpath(__file__))
cfgPath = os.path.join(syspath,'config.json')
config = None
with open(cfgPath) as config_file:
    config = json.load(config_file)

def writeJson(path, dict):
        logging.info("ConfigGLobals: write jsonFile...")
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
with open(dbPath) as dbFile:
    db = json.load(dbFile)

def writeDb():
    writeJson(dbPath, db)
