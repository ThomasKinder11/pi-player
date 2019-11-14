'''
This is the main menu using the Kivy frame work. All other Gui Elements
are added here. This code is also respnisble for setting up keyhandling
and key processing for all selectable elements in the GUI
'''
import logging
import os

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.stacklayout import StackLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

import control_tree
import includes
from selectable_items import SelectableTabbedPanelHeader
from screensaver import ScreenSaver
from menu_settings import MenuSettings
from menu_video import FileList
from menu_osd import MenuOSD
from menu_playlist import MenuPlaylist
from key_handler import KeyHandler
from dialog import DialogHandler
from menu_system import MenuSystem
from control_tree import selectId as selectId


class IshaGui(StackLayout):
    '''This is the top object of the Gui'''
    osd = None

    def resize(self, widget, value):
        '''resize callback when width/height are chaning'''
        self.screens.height = Window.height - self.osd.height

    def __init__(self, **kwargs):
        super(IshaGui, self).__init__(**kwargs)

        self.osd = MenuOSD(id=str(selectId['osd']))
        self.screens = IshaPiScreens(osd=self.osd)

        self.screens.size_hint_y = None
        self.screens.height = Window.height - self.osd.height

        self.add_widget(self.screens)
        self.add_widget(self.osd)

        self.bind(height=self.resize)

class IshaPiScreens(ScreenManager):
    '''
    The screen manager allows us to swith between multiple defined scrrens.
    This feature is used to implement:
        1: Main menu
        2: Screen Saver black screen
        3: OSD for videos
    '''
    menuOSD = None
    menuScreen = None
    menuScreenSaver = None
    menuOSDScreen = None
    osd = None

    def __init__(self, **kwargs):
        self.osd = kwargs.pop('osd', None)

        super(IshaPiScreens, self).__init__(**kwargs)

        self.transition = NoTransition()
        self.menuScreenSaver = Screen(name="blackscreen")
        self.menuScreen = Screen(name="main_menu")

        self.mainMenu = Menu(root=self, osd=self.osd)
        self.menuScreen.add_widget(self.mainMenu)
        self.add_widget(self.menuScreen)
        self.add_widget(self.menuScreenSaver)
        self.current = "main_menu"


class Menu(StackLayout, TabbedPanel):
    '''This is the tab view pannel which will show all gui lements except the OSD'''
    selectableWidgets = {}
    tbHeads = []
    curId = 100
    lastId = None
    root = None
    screenSaver = None
    menuOSD = None
    #callbackPlayEnd = []

    def _globalKeyHandler(self, keycode):

        #volume control
        if keycode[1] == "+":
            self.osd.volumeUp(None)
            return

        if keycode[1] == "-":
            self.osd.volumeDown(None)
            return

        if keycode[1] == "m":
            self.osd.muteToggle(None)
            self.selectableWidgets[selectId['pFiles']].ctrlQueue.put({'cmd':'end'})
            return

    _keyHandledMextId = False
    def _keyHanlder(self, cmdList):
        #cmdList is a list of dictonaries containing the command being executed
        #cmdList can be specified as None in control tree which means nothing to do
        if cmdList is None:
            return

        for cmd in cmdList:

            #Check if cmd is also a list, if so recursively we will execute
            #logging.debug("_keyHandler: going to execute command = {}".format(cmd))
            if isinstance(cmd, list):
                self._keyHanlder(cmd)
                continue

            #last entry, this will stop execution
            if 'nextid' in cmd and  not self._keyHandledMextId:
                self._keyHandledMextId = True
                self.curId = cmd['nextid']
                return

            if not all(k in cmd for k in ("id", "func")):
                cmd = "_keyHandler: You did not specify id/func for tree elemnt "
                cmd = cmd + "with id = {} ".format(self.curId)
                logging.error(cmd)
                return

            tmpId = cmd['id']
            func = cmd['func']

            #args attribute is optional, can be used when we want to pass something to callback
            args = {}
            if 'args' in cmd:
                args = cmd['args']

            #add user defined arguments of selectable widget to args passed to callback
            if self.selectableWidgets[tmpId].user is not None:
                for item in self.selectableWidgets[tmpId].user:
                    args[item] = self.selectableWidgets[tmpId].user[item]


            #Execute build in fucntions/object functions
            if func == "switch":#build-in-switch-tabpannel
                self.switch_to(self.selectableWidgets[tmpId], False)
            else:
                ret = getattr(self.selectableWidgets[tmpId], func)(args)

                if ret and 'true' in cmd: #execute ret functions if specified
                    self._keyHanlder(cmd['true'])

                if not ret and 'false' in cmd: #execute ret functions if specified
                    self._keyHanlder(cmd['false'])


    def osdDisable(self, args):
        '''Switche control back to last element after OSD was displayed'''
        self.curId = self.lastId

    def osdEnable(self, args):
        '''Before switching to the OSD remember the current selected element'''
        self.lastId = self.curId
        self.curId = 200

    def _keyDown(self, keycode):
        '''Callback function for keyboard events. All key handling is done here.'''
        if self.screenSaver.active and self.screenSaver.ena:
            self.screenSaver.resetTime()
            return 0

        self.screenSaver.resetTime()

        msg = "Menu: Key Pressed [{}] ".format(keycode)
        msg = msg + "on element with curId = {}".format(self.curId)
        logging.debug(msg)

        self._globalKeyHandler(keycode)

        if keycode[1] in self.controlTree[self.curId]:
            self._keyHandledMextId = False #prepare keyHandler function
            self._keyHanlder(self.controlTree[self.curId][keycode[1]])
            return 0

        return -1

    def _findSelectableChildren(self, children):
        if not children:
            return

        for child in children:
            try:
                self._findSelectableChildren(child.children)
                if child and child.isSelectable:
                    self.selectableWidgets[int(child.id)] = child
            except Exception as allExceptions:
                pass



    def _onUpdateRunTime(self, value):
        self.osd.runtime.text = value

    def _warningPlay(self, args):
        logging.error("Warning: play somthing something something")


    def __init__(self, **kwargs):
        self.root = kwargs.pop('root', "None")
        self.osd = kwargs.pop('osd', "None")

        kwargs["do_default_tab"] = False #always disable the default tab
        super(Menu, self).__init__(**kwargs)

        tmp = KeyHandler()
        tmp.onPress = self._keyDown

        #Setup tabview for main menu
        self.tab_width = 150 + 10
        self.tab_height = 60


        self.selectableWidgets[selectId['settings']] = SelectableTabbedPanelHeader(
            id=str(selectId['settings']),
        )
        self.selectableWidgets[selectId['settings']].background_normal = "atlas://resources/img/pi-player/settings"
        self.selectableWidgets[selectId['settings']].background_down = "atlas://resources/img/pi-player/settings_select"

        self.selectableWidgets[selectId['videos']] = SelectableTabbedPanelHeader(
            id=str(selectId['videos']),
        )
        self.selectableWidgets[selectId['videos']].background_normal = "atlas://resources/img/pi-player/video"
        self.selectableWidgets[selectId['videos']].background_down = "atlas://resources/img/pi-player/video_select"


        self.selectableWidgets[selectId['music']] = SelectableTabbedPanelHeader(
            id=str(selectId['music']),
        )
        self.selectableWidgets[selectId['music']].background_normal = "atlas://resources/img/pi-player/music"
        self.selectableWidgets[selectId['music']].background_down = "atlas://resources/img/pi-player/music_select"


        self.selectableWidgets[selectId['playlist']] = SelectableTabbedPanelHeader(
            id=str(selectId['playlist']),
        )
        self.selectableWidgets[selectId['playlist']].background_normal = "atlas://resources/img/pi-player/playlist"
        self.selectableWidgets[selectId['playlist']].background_down = "atlas://resources/img/pi-player/playlist_select"

        self.selectableWidgets[selectId['system']] = SelectableTabbedPanelHeader(id=str(selectId['system']))

        self.selectableWidgets[selectId['system']].background_normal = "atlas://resources/img/pi-player/power"
        self.selectableWidgets[selectId['system']].background_down = "atlas://resources/img/pi-player/power_select"


        #for i in range(len(self.selectableWidgets)):
        self.add_widget(self.selectableWidgets[selectId['system']])
        self.add_widget(self.selectableWidgets[selectId['videos']])
        self.add_widget(self.selectableWidgets[selectId['music']])
        self.add_widget(self.selectableWidgets[selectId['playlist']])
        self.add_widget(self.selectableWidgets[selectId['settings']])

        self.selectableWidgets[selectId['settings']].content = MenuSettings()

        #Setup Video menu
        self.selectableWidgets[selectId['vFile']] = FileList(
            id=str(selectId['vFile']),
            rootdir=includes.config['video']['rootdir'],
            enaColor=includes.styles['enaColor0'],
            bar_width=10,
            size_hint=(1, None),
            size=(Window.width, Window.height),
            supportedTypes=includes.config['video']['types'],
            screenmanager=self.root,
            selectFirst=False,
            type="video"
        )
        self.selectableWidgets[selectId['videos']].content = self.selectableWidgets[selectId['vFile']]

        #Setup Audio menu
        self.selectableWidgets[selectId['mFiles']] = FileList(
            id=str(selectId['mFiles']),
            rootdir=includes.config['audio']['rootdir'],
            enaColor=includes.styles['enaColor0'],
            bar_width=10,
            size_hint=(1, None),
            size=(Window.width, Window.height),
            supportedTypes=includes.config['audio']['types'],
            screenmanager=self.root,
            selectFirst=False
        )
        self.selectableWidgets[selectId['music']].content = self.selectableWidgets[selectId['mFiles']]


        #Setup Playlist menu
        self.selectableWidgets[selectId['pFiles']] = MenuPlaylist(
            id=str(selectId['pFiles']),
            screenmanager=self.root
        )
        self.selectableWidgets[selectId['pFiles']].osdEnable = self.osdEnable
        self.selectableWidgets[selectId['pFiles']].osdDisable = self.osdDisable
        self.selectableWidgets[selectId['pFiles']].osdColorIndicator = self.osd.setColorIndicator

        self.selectableWidgets[selectId['playlist']].content = self.selectableWidgets[selectId['pFiles']]


        #Setup the menu for system notifications and system operations like shutdown
        self.menuSystem = MenuSystem()
        self.selectableWidgets[selectId['system']].content = self.menuSystem #self.handler
        self.selectableWidgets[selectId['systemMsg']] = self.menuSystem.handler
        self.selectableWidgets[selectId['systemBtn']] = self.menuSystem.btn

        #Find all the children which are selectble and can be controlled by keyboard
        self._findSelectableChildren(self.selectableWidgets[selectId['settings']].content.children)
        self._findSelectableChildren(self.selectableWidgets[selectId['videos']].content.children)
        self.selectableWidgets[200] = self.osd

        self.controlTree = control_tree.CONTROL_TREE
        self.curId = selectId['system'] # set start id

        #do not allow down press on empty list
        if len(self.selectableWidgets[selectId['mFiles']].layout.children) <= 0:
            self.controlTree[2]['down'] = None

        try:
            self.selectableWidgets[self.curId].enable(None)
        except Exception as allExceptions:
            logging.error("Menu: cannot find default widget...")

        #setup the screen saver and also make it available as global object
        self.screenSaver = ScreenSaver(self.root, "blackscreen", "main_menu")
        self.screenSaver.enable()
        includes.screenSaver = self.screenSaver

        #set player callbacks
        includes.player.onPlayEnd = self.selectableWidgets[selectId['pFiles']].onPlayerEnd
        includes.player._onUpdateRunTime = self._onUpdateRunTime

        #Setup OSD callback for passing enter command to playlist
        self.osd.onPlaylistEnter = self.selectableWidgets[selectId['pFiles']].enter
        self.osd.btnPlay.onEnter =  self.selectableWidgets[selectId['pFiles']].play
        self.osd.btnPause.onEnter =  self.selectableWidgets[selectId['pFiles']].pause
        self.osd.btnPrevious.onEnter =  self.selectableWidgets[selectId['pFiles']].previous
        self.osd.btnNext.onEnter =  self.selectableWidgets[selectId['pFiles']].next
        self.osd.btnStop.onEnter =  self.selectableWidgets[selectId['pFiles']].abort

        #Setup video/audio view callbacks
        tmp = self.selectableWidgets[selectId['pFiles']].startVirtualSingle
        self.selectableWidgets[selectId['vFile']]._onEnterPlayer = tmp
        self.selectableWidgets[selectId['mFiles']]._onEnterPlayer = tmp
