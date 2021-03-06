from player import *
from screensaver import *
import os
import logging
import json
from kivy.utils import get_color_from_hex as hexColor

#Just make sure its not causing error redefininf build-in
defined = True

#Color definition
colors = {
    'gray': (0.4,0.4,0.4,1),
    'darkgray': (0.2,0.2,0.2,1),
    'darkestgray': (0.1,0.1,0.1,1),
    'defaultGray': hexColor('#303030'),
    'red': (0.5,0.0,0.0,0.8),
    'lightred': (0.8,0.2,0.2,0.3),
    'black' : (0, 0, 0, 1),
    'darkblue': hexColor('#2c2c57'),
    'blue' : (0.5, 0.5, 1, 1),
    'oldblue': hexColor('#0f85a5'),
    'lightblue' : hexColor('#035972'),
    'orange' : (1,0.5,0.2,0.5),
    'ishaOrange' : hexColor('#F15B28'),
    #error message colors
    'errMsgHead' : hexColor('#6c5d53'),
    'errMsgText' : hexColor('#ffffff'),
    'errMsgSidebar' : hexColor('#483e37'),
    'errMsgContent' : hexColor('#917c6f'),
    #warning message colors
    'warnMsgHead' : hexColor('#536c5d'),
    'warnMsgText' : hexColor('#ffffff'),
    'warnMsgSidebar' : hexColor('#37483e'),
    'warnMsgContent' : hexColor('#6f917c'),
    #info message colors
    'infoMsgHead' : hexColor('#216778'),
    'infoMsgText' : hexColor('#ffffff'),
    'infoMsgSidebar' : hexColor('#164450'),
    'infoMsgContent' : hexColor('#2c89a0'),
    'msgBorder' : hexColor('#303030'),
    # #error message colors
    # 'errMsgHead' : hexColor('#ffc8be'),
    # 'errMsgText' : hexColor('#000000'),
    # 'errMsgSidebar' : hexColor('#fda798'),
    # 'errMsgContent' : hexColor('#ffd8d2'),
    # #warning message colors
    # 'warnMsgHead' : hexColor('#ffe78d'),
    # 'warnMsgText' : hexColor('#000000'),
    # 'warnMsgSidebar' : hexColor('#ffd965'),
    # 'warnMsgContent' : hexColor('#ffeeaa'),
    # #info message colors
    # 'infoMsgHead' : hexColor('#5599ff'),
    # 'infoMsgText' : hexColor('#000000'),
    # 'infoMsgSidebar' : hexColor('#2a7fff'),
    # 'infoMsgContent' : hexColor('#80b3ff'),
    # 'msgBorder' : hexColor('#666666')
}

styles = {
    #colors
    'defaultEnaColor': colors['oldblue'],
    'defaultBg': colors['black'],
    'enaColor0': colors['oldblue'],
    'enaColor1': colors['orange'],
    'warning': colors['lightred'],
    'defaultFiller': colors['lightblue'],
    #'itemColor0': colors['darkgray'],
    'itemColor0': colors['defaultGray'],
    'itemColor1': colors['defaultGray'],
    #'itemColor1': colors['darkestgray'],
    'volumeIndicatorBG': colors['gray'],
    'volumeIndicatorColor': colors['blue'],
    'headerColor0': colors['darkblue'],
    'headerColor1': colors['gray'],
    #sizes
    'selectItemHeight': 80,
    "fontSize": "25sp",
    "playlistHeadHeight": 40,
    #Dailogs
    'dialogBorderHeight': 5,
    #Playlist color Indicator
    'pListIndiactorHeight':15,
    'plistIndicatorColor':colors['oldblue']
}




#Media player instance we can use in all modules
player = Player()

#configuration file
syspath = os.path.dirname(os.path.realpath(__file__))
cfgPath = os.path.join(syspath,'config.json')
config = None
with open(cfgPath) as config_file:
    config = json.load(config_file)

#logging.error(config)

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

#
# Some utilities and helpers
#
def clipInt(value, min, max):
    if value > max:
        return max

    if value < min:
        return min

    return value
