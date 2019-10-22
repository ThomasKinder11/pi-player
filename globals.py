from player import *
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
    f = open(cfgPath, "w")
    f.write(json.dumps(config, sort_keys=True, indent=4))
    f.close()
