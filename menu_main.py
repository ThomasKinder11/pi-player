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

if os.name == 'nt':
    import keyboard

import control_tree
import includes
from selectable_items import SelectableTabbedPanelHeader
from screensaver import ScreenSaver
from menu_settings import MenuSettings
from menu_video import FileList
from menu_osd import MenuOSD
from menu_playlist import MenuPlaylist



if os.name == "posix":
    from key_handler import KeyHandler


class IshaGui(StackLayout):
    '''This is the top object of the Gui'''
    osd = None

    def resize(self, widget, value):
        '''resize callback when width/height are chaning'''
        self.screens.height = Window.height - self.osd.height

    def __init__(self, **kwargs):
        super(IshaGui, self).__init__(**kwargs)

        self.osd = MenuOSD(id="200")
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
            self.selectableWidgets[40000].ctrlQueue.put({'cmd':'end'})
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


    def osdDisable(self, args):
        '''Switche control back to last element after OSD was displayed'''
        self.curId = self.lastId

    def osdEnable(self, args):
        '''Before switching to the OSD remember the current selected element'''
        self.lastId = self.curId
        self.curId = 200



    def _keyDown(self, keycode):
        '''Callback function for keyboard events. All key handling is done here.'''
        logging.error("_keyDowm called with keycode = {}".format(keycode))
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

    def onPress(self, key):
        '''callback fucntion when any keyboard button is pressed. It will analyze keycomand'''
        scancodes = {}
        #if os.name == "nt":
        scancodes[77] = "right"
        scancodes[75] = "left"
        scancodes[72] = "up"
        scancodes[80] = "down"
        scancodes[-166] = "browser back"
        scancodes[-175] = "volume up"
        scancodes[-174] = "volume down"
        scancodes[-173] = "volume mute"
        # elif os.name == "posix":
        #     scancodes[106] = "right"
        #     scancodes[105] = "left"
        #     scancodes[103] = "up"
        #     scancodes[108] = "down"
        #     scancodes[-166] = "browser back"
        #     scancodes[-175] = "volume up"
        #     scancodes[-174] = "volume down"
        #     scancodes[-173] = "volume mute"

        scancodes[28] = "enter"
        scancodes[27] = "+"
        scancodes[53] = "-"
        scancodes[50] = "m"

        tmpId = key.scan_code

        if tmpId in scancodes:
            keycode = [tmpId, scancodes[tmpId]]
            self._keyDown(keycode)

    def _onUpdateRunTime(self, value):
        self.osd.runtime.text = value


    def __init__(self, **kwargs):
        self.root = kwargs.pop('root', "None")
        self.osd = kwargs.pop('osd', "None")

        kwargs["do_default_tab"] = False #always disable the default tab
        super(Menu, self).__init__(**kwargs)

        if os.name == 'posix':
            logging.error("´´´´´´´´´´´´ßßßßßßßßßßß: Posix keyhandler")
            tmp = KeyHandler()
            tmp.onPress = self._keyDown
        else:
            keyboard.on_press(self.onPress)


        #Setup tabview for main menu
        self.tab_width = 100
        self.tab_height = 40

        self.selectableWidgets[0] = SelectableTabbedPanelHeader(
            text="Settings",
            id="000",
            enaColor=includes.colors['blue']
        )

        self.selectableWidgets[1] = SelectableTabbedPanelHeader(
            text="Video",
            id="001",
            enaColor=includes.colors['blue']
        )

        self.selectableWidgets[2] = SelectableTabbedPanelHeader(
            text="Music",
            id="002",
            enaColor=includes.colors['blue']
        )

        self.selectableWidgets[3] = SelectableTabbedPanelHeader(
            text="Playlist",
            id="003",
            enaColor=includes.colors['blue']
        )

        self.selectableWidgets[4] = SelectableTabbedPanelHeader(id="004")
        self.selectableWidgets[4].background_normal = "./resources/img/power.png"
        self.selectableWidgets[4].background_down = "./resources/img/power_select.png"


        #for i in range(len(self.selectableWidgets)):
        self.add_widget(self.selectableWidgets[4])
        self.add_widget(self.selectableWidgets[1])
        self.add_widget(self.selectableWidgets[2])
        self.add_widget(self.selectableWidgets[3])
        self.add_widget(self.selectableWidgets[0])

        self.selectableWidgets[0].content = MenuSettings()

        #Setup Video menu
        self.selectableWidgets[20000] = FileList(
            id="20000",
            rootdir=includes.config[os.name]['video']['rootdir'],
            enaColor=includes.colors['blue'],
            bar_width=10,
            size_hint=(1, None),
            size=(Window.width, Window.height),
            supportedTypes=includes.config[os.name]['video']['types'],
            screenmanager=self.root,
            selectFirst=False,
            type="video"
        )
        self.selectableWidgets[1].content = self.selectableWidgets[20000]

        #Setup Audio menu
        self.selectableWidgets[30000] = FileList(
            id="30000",
            rootdir=includes.config[os.name]['audio']['rootdir'],
            enaColor=includes.colors['blue'],
            bar_width=10,
            size_hint=(1, None),
            size=(Window.width, Window.height),
            supportedTypes=includes.config[os.name]['audio']['types'],
            screenmanager=self.root,
            selectFirst=False
        )
        self.selectableWidgets[2].content = self.selectableWidgets[30000]

        #Setup Playlist menu
        self.selectableWidgets[40000] = MenuPlaylist(
            id="40000",
            screenmanager=self.root
        )
        self.selectableWidgets[40000].osdEnable = self.osdEnable
        self.selectableWidgets[40000].osdDisable = self.osdDisable
        self.selectableWidgets[40000].osdColorIndicator = self.osd.setColorIndicator

        self.selectableWidgets[3].content = self.selectableWidgets[40000]


        #Find all the children which are selectble and can be controlled by keyboard
        self._findSelectableChildren(self.selectableWidgets[0].content.children)
        self._findSelectableChildren(self.selectableWidgets[1].content.children)
        self.selectableWidgets[200] = self.osd

        self.controlTree = control_tree.CONTROL_TREE
        self.curId = 4 # set start id

        try:
            self.selectableWidgets[self.curId].enable(None)
        except Exception as allExceptions:
            logging.error("Menu: cannot find default widget...")

        #setup the screen saver and also make it available as global object
        self.screenSaver = ScreenSaver(self.root, "blackscreen", "main_menu")
        self.screenSaver.enable()
        includes.screenSaver = self.screenSaver

        #set player
        includes.player.onPlayEnd = self.selectableWidgets[40000].onPlayerEnd
        includes.player._onUpdateRunTime = self._onUpdateRunTime

        #Setup OSD callback for passing enter command to playlist
        self.osd.onPlaylistEnter = self.selectableWidgets[40000].enter
        self.osd.playlistAbort = self.selectableWidgets[40000].abort
        self.osd.playlistPrevious = self.selectableWidgets[40000].previous
        self.osd.playlistNext = self.selectableWidgets[40000].next
        self.osd.onEnterPause = self.selectableWidgets[40000].pause
        self.osd.isPaused = self.selectableWidgets[40000].isPaused
        self.osd.hasNextTrack = self.selectableWidgets[40000].hasNextTrack
        self.osd.hasPreviousTrack = self.selectableWidgets[40000].hasPreviousTrack

        #Setup video/audio view callbacks
        tmp = self.selectableWidgets[40000].startVirtualSingle
        self.selectableWidgets[20000]._onEnterPlayer = tmp
        self.selectableWidgets[30000]._onEnterPlayer = tmp
