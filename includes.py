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
    'pListIndiactorHeight':25,
    'plistIndicatorColor':colors['darkblue']
}

#
# Some utilities and helpers
#
def clipInt(value, min, max):
    '''Set lower and uper limits of integer values'''
    if value > max:
        return max

    if value < min:
        return min

    return value

def isRemoteCtrlCmd(cmd):
    '''check if cmd is a valid json command, TODO: we might remove this'''
    if not 'cmd' in cmd:
        return False

    return True

def writeJson(path, dict):
    '''write the configuration into a json file'''
    try:
        f = open(path, "w")
    except FileNotFoundError as e:
        try:
            os.makedirs(os.path.dirname(path))
        except PermissionError as e:
            logging.error("Includes: writeJson: No permissions to write JSON file")
            return
    except PermissionError as e:
        logging.error("Includes: writeJson: No permissions to write JSON file")
        return

    f.write(json.dumps(dict, sort_keys=True, indent=4))
    f.close()

def openDb(dbPath):
    try:
        with open(dbPath) as dbFile:
            db = json.load(dbFile)
    except FileNotFoundError as e:
        try:
            f = open(dbPath, "w+")
            f.write('''{
                        "runtime":0
                        }''')
            f.close()
        except PermissionError as e:
            logging.error("Includes: openDb: No permissions to write database file")
            return None
        except:
            logging.error("Includes: openDb: database error")
            return None

        with open(dbPath) as dbFile:
            db = json.load(dbFile)

        return db




#Media player instance we can use in all modules
player = Player()

#configuration file and defualt config
cfgPath = "/opt/config/imc_config.json"

defaultCfg = {}
defaultCfg['tmpdir'] = "/tmp"
defaultCfg['music'] = {
    "rootdir": "/mnt/Ishamedia",
    "types": "mp3,wav",
    "autoplay": "false"
}
defaultCfg["video"] = {
    "rootdir": "/mnt/Ishamedia",
    "types": "mp4",
    "autoplay": "false"
}
defaultCfg["settings"] = {
    "osdTime": 10,
    "runtimeInterval": 1,
    "screensaverTime": 90
}
defaultCfg["httpServerIp"] = {
    "ip":"127.0.0.1",
    "port":"11111"
}
defaultCfg["ipcOsdPort"] = 40001
defaultCfg["ipcWmPort"] = 40002

if not os.path.exists(cfgPath):
    writeJson(cfgPath, defaultCfg)
    config = defaultCfg
else:
    try:
        with open(cfgPath) as cfgFile:
            tmp = json.load(cfgFile)
            config = defaultCfg.update(tmp)
    except:
        logging.warning("IncludesConfig: could not load config file. Use default config")
        config = defaultCfg

def writeConfig():
    writeJson(cfgPath, config)

#Global instance of screen saver
screenSaver = None #will be initialized by main-menu

#database, bsically a json file which we read and write
dbPath = "/opt/config/imc_database.json"
db = None
db = openDb(dbPath)



def writeDb():
    writeJson(dbPath, db)
