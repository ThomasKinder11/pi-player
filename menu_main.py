from isha_pi_kivy import *
from menu_settings import MenuSettings
from menu_video import MenuVideo
import logging
import json, os
import control_tree
import globals
from menu_osd import *

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
        self.menuScreen = Screen(name="main_menu")
        self.menuScreen.add_widget(Menu(root=self))
        self.add_widget(self.menuScreen)

        self.menuScreenSaver = Screen(name="screensaver")
        self.add_widget(self.menuScreenSaver)

        self.menuOSDScreen = Screen(name="osd")
        #osdLayout = StackLayout(orientation='lr-bt')
        #osdLayout.add_widget(Button(text="This is the osd", size_hint_y=None, height=50))
        #menuOSD.add_widget(osdLayout)
        self.menuOSD = MenuOSD(id="0")
        self.menuOSDScreen.add_widget(self.menuOSD)
        self.add_widget(self.menuOSDScreen)


class Menu(StackLayout, TabbedPanel):
    selectableWidgets = {}
    tbHeads = []
    curId = 100
    nextId = None
    root = None


    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._keyDown)
        self._keyboard = None

    def _clearIdleTimer(self):
        pass

    """
    Callback function for keyboard events. All key handling is done here.
    """
    def _keyDown(self, keyboard, keycode, text, modifiers):

        logging.info("Menu: Key Pressed [{}] on element with curId = {}".format(keycode, self.curId))

        #map button b to enable/disable screensaver"
        if keycode[1] == 'b':
            if self.root.current != 'screensaver':
                self.root.current = "screensaver"
            else:
                self.root.current = "main_menu"
            return

        #-----------------------------------------------------------------------
        # Execute selectable widget specific keymappings
        #-----------------------------------------------------------------------

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


        #-----------------------------------------------------------------------
        # Execute selectable widget specific keymappings
        #-----------------------------------------------------------------------

        #get the controll tree entry for the currently selected item for execution
        tmp = None
        try:
            tmp = self.controlTree[self.curId][keycode[1]]
            if tmp == None: #do not do anything if None is specified
                return
        except:
            logging.error("Menu: ControlTree has no element with id = {} / or element did not specify keycode = {}".format(self.curId, keycode[1]))
            return

        #process the comands defined in control tree
        tmpId = -1
        ret =  False
        tmpNextId = None

        if len(tmp) > 0:
            if "nextid" in tmp[-1]:
                self.nextId = tmp[-1]['nextid']
        else:
            logging.warning("menu_main: the controlTree entry 'nextid' is not set...")
            return

        for item in tmp:
            logging.info("Menu: execute comand = {}".format(item))

            if ('id' in item) and ('func' in item):
                if item['func'] == "switch":
                    tmpId = item['id']
                    self.switch_to(self.selectableWidgets[tmpId], False)
                else:
                    try:
                        tmpId = item['id']
                        ret = getattr(self.selectableWidgets[tmpId], item['func'])()
                    except:
                        logging.error("Menu: id = {} not in tree or widget list...".format(tmpId))


                    if ret:
                        self.curId = self.nextId
                        try:
                            tr = item['true']
                            tmpId = item['id']
                            self.nextId = tr['nextid']
                            getattr(self.selectableWidgets[tr['id']], tr['func'])()

                        except:
                            logging.debug("Menu: no true action defined...")

                    else:
                        logging.info("Menu: execute false return value...")
                        self.curId = self.nextId
                        try:
                            tr = item['false']
                            tmpId = item['id']
                            getattr(self.selectableWidgets[tr['id']], tr['func'])()

                        except:
                            logging.debug("Menu: no false action defined...")


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
        self.root = kwargs.pop('root', None)
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
        #self.selectableWidgets[20000] = SelectListView(id="20000", enaColor=[0.5,0.5,1,1], bar_width=10, size_hint=(1, None), size=(Window.width, Window.height))#MenuVideo()

        #Setup Video menu
        self.selectableWidgets[20000] = MenuVideo(
            id="20000",
            rootdir=globals.config[os.name]['video']['rootdir'],
            enaColor=[0.5,0.5,1,1],
            bar_width=10,
            size_hint=(1, None),
            size=(Window.width, Window.height),
            supportedTypes=globals.config[os.name]['video']['types'],
            screenmanager=self.root
        )

        self.selectableWidgets[1].content = self.selectableWidgets[20000]

        #Find all the children which are selectble and can be controlled by keyboard
        self._findSelectableChildren(self.selectableWidgets[0].content.children)
        self._findSelectableChildren(self.selectableWidgets[1].content.children)

        self.controlTree = control_tree.controlTree
        self.curId = 0 # set start id
        try:
            self.selectableWidgets[self.curId].enable()
        except:
            logging.error("Menu: cannot find default widget...")
