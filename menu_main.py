from isha_pi_kivy import *
from screensaver import ScreenSaver
from menu_settings import MenuSettings
from menu_video import FileList
import logging
import json, os
import control_tree
import globals
from menu_osd import *
from menu_playlist import *

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.stacklayout import StackLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

"""
The screen manager allows us to swith between multiple defined scrrens.
This feature is used to implement:
    1: Main menu
    2: Screen Saver black screen
    3: OSD for videos
"""
class IshaPiScreens(ScreenManager):
    menuOSD = None
    menuScreen = None
    menuScreenSaver = None
    menuOSDScreen = None

    def __init__(self, **kwargs):
        super(IshaPiScreens, self).__init__(**kwargs)

        self.transition=NoTransition()


        self.menuScreenSaver = Screen(name="screensaver")

        self.menuOSDScreen = Screen(name="osd")
        self.menuOSD = MenuOSD(id="200")
        self.menuOSDScreen.add_widget(self.menuOSD)

        self.add_widget(self.menuOSDScreen)

        self.menuScreen = Screen(name="main_menu")
        self.menuScreen.add_widget(Menu(root=self))
        self.add_widget(self.menuScreen)

        self.add_widget(self.menuScreenSaver)
        self.current = "main_menu"



class Menu(StackLayout, TabbedPanel):
    selectableWidgets = {}
    tbHeads = []
    curId = 100
    nextId = None
    lastId = None
    root = None
    screenSaver = None
    menuOSD = None
    keyProcessing = False
    playbackFirst = True

    def _globalKeyHandler(self, keycode):

        #map key o to switch to OSD - this is only needed for debugging and can be removed
        if keycode[1] == 'o':
            self.root.current = "osd"
            return

        #volume control
        if keycode[1] == "+":
            self.root.menuOSD.volumeUp()
            return

        if keycode[1] == "-":
            self.root.menuOSD.volumeDown()
            return

        if keycode[1] == "m":
            self.root.menuOSD.muteToggle()
            return

    _keyHandledMextId = False
    def _keyHanlder(self, cmdList):
        #cmdList is a list of dictonaries containing the command being executed
        #cmdList can be specified as None in control tree which means nothing to do
        if cmdList == None:
            return 0

        for cmd in cmdList:
            #Check if cmd is also a list, if so recursively we will execute
            if isinstance(cmd,list):
                self._keyHanlder(cmd)
                continue

            if 'nextid' in cmd and self._keyHandledMextId == False: #last entry, this will stop execution
                self._keyHandledMextId = True
                self.curId = cmd['nextid']
                logging.debug("_keyHandler: nextid has been processed...")
                return 0

            if not (all(k in cmd for k in ("id","func"))):
                logging.error("_keyHandler: You did not specify id/func for tree elemnt with id = {} ".format(self.curId))
                return -1

            id = cmd['id']
            func = cmd['func']

            #args attribute is optional, can be used when we want to pass something to callback
            args = None
            if 'args' in cmd:
                args = cmd['args']

            #Execute build in fucntions/object functions
            if func == "switch":#build-in-switch-tabpannel
                self.switch_to(self.selectableWidgets[id], False)
            else:
                ret = getattr(self.selectableWidgets[id], func)(args)

                if ret and 'true' in cmd: #execute ret functions if specified
                    self._keyHanlder(cmd['true'])

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._keyDown)
        self._keyboard = None

    """
    _onPlayEnd : callback which is called by player after playback has been
                 finished. This can be used to control playlist etc.
    """
    def _onPlayEnd(self):
        self.root.current = "main_menu"
        self.screenSaver.enable()
        self.curId  = self.lastId

    def _onEnterPlayer(self, args):
        logging.info("_onEnterPlayer: start playing the file...")
        self.screenSaver.disable()
        self.root.current = "osd"

        #switch menu controll to osd...

        #Wait until current pressed button commands are execute completely
        # while self.keyProcessing:
        #     continue# = True

        self.lastId = self.curId
        self.curId = 200
        #self.nextId = 200

        self.playbackFirst = True
        path = args.pop("path", None)
        player.play(path)


    """
    Callback function for keyboard events. All key handling is done here.
    """
    def _keyDown(self, keyboard, keycode, text, modifiers):
    #do not process key strokes when player is playing something
        self.keyProcessing = True

        if self.screenSaver.active and self.screenSaver.ena:
            self.screenSaver.resetTime()
            self.keyProcessing = False
            return

        self.screenSaver.resetTime()
        logging.info("Menu: Key Pressed [{}] on element with curId = {}".format(keycode, self.curId))

        self._globalKeyHandler(keycode)

        if keycode[1] in self.controlTree[self.curId]:
            self._keyHandledMextId = False #prepare keyHandler function
            self._keyHanlder(self.controlTree[self.curId][keycode[1]])
            self.keyProcessing = False

            return 0
        else:
            self.keyProcessing = False
            return -1

    def _findSelectableChildren(self, children):
        if not children:
            return

        for child in children:
            try:
                self._findSelectableChildren(child.children)
                if child and child.isSelectable:
                    self.selectableWidgets[int(child.id)] = child
            except:
                pass

    def __init__(self, **kwargs):
        self.root = kwargs.pop('root', "None")
        #self.menuOSD = kwargs.pop('osd', "None")

        kwargs["do_default_tab"] = False #always disable the default tab
        super(Menu, self).__init__(**kwargs)

        #Keyboard binding
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._keyDown)

        #Setup tabview for main menu
        self.selectableWidgets[0]=SelectableTabbedPanelHeader(text="Settings", id="000", enaColor=[0.5,0.5,1,1])
        self.selectableWidgets[1]=SelectableTabbedPanelHeader(text="Video", id="001", enaColor=[0.5,0.5,1,1])
        self.selectableWidgets[2]=SelectableTabbedPanelHeader(text="Music", id="002", enaColor=[0.5,0.5,1,1])
        self.selectableWidgets[3]=SelectableTabbedPanelHeader(text="Playlist", id="003", enaColor=[0.5,0.5,1,1])

        for i in range(len(self.selectableWidgets)):
            self.add_widget(self.selectableWidgets[i])

        self.selectableWidgets[0].content = MenuSettings()

        #Setup Video menu
        self.selectableWidgets[20000] = FileList(
            id="20000",
            rootdir=globals.config[os.name]['video']['rootdir'],
            enaColor=[0.5,0.5,1,1],
            bar_width=10,
            size_hint=(1, None),
            size=(Window.width, Window.height),
            supportedTypes=globals.config[os.name]['video']['types'],
            screenmanager=self.root
        )
        self.selectableWidgets[20000]._onEnterPlayer = self._onEnterPlayer
        self.selectableWidgets[1].content = self.selectableWidgets[20000]

        #Setup Audio menu
        self.selectableWidgets[30000] = FileList(
            id="30000",
            rootdir=globals.config[os.name]['audio']['rootdir'],
            enaColor=[0.5,0.5,1,1],
            bar_width=10,
            size_hint=(1, None),
            size=(Window.width, Window.height),
            supportedTypes=globals.config[os.name]['audio']['types'],
            screenmanager=self.root
        )

        self.selectableWidgets[2].content = self.selectableWidgets[30000]

        #Setup Playlist menu
        self.selectableWidgets[40000] = MenuPlaylist(
            id="40000",
            screenmanager=self.root
        )

        self.selectableWidgets[3].content = self.selectableWidgets[40000]


        #Find all the children which are selectble and can be controlled by keyboard
        self._findSelectableChildren(self.selectableWidgets[0].content.children)
        self._findSelectableChildren(self.selectableWidgets[1].content.children)
        self.selectableWidgets[200] = self.root.menuOSD


        self.controlTree = control_tree.controlTree
        self.curId = 0 # set start id
        self.lastId = self.curId

        try:
            self.selectableWidgets[self.curId].enable(None)
        except:
            logging.error("Menu: cannot find default widget...")

        #setup the screen saver and also make it available as global object
        self.screenSaver = ScreenSaver(self.root, "screensaver", "main_menu")
        globals.screenSaver = self.screenSaver

        #set player
        player.onPlayEnd = self._onPlayEnd
