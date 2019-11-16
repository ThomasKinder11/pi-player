'''
This is the implementation of the media players on screen display
to control the playback of the media files. The main object
is the MenuOSD() class which can be added to Kivy gui applications.

This creates a 50px high button bar, under under it a 5px high
border which color can be changed to display different states of
the software, e.g. the color could be changed to differentiate
between screen saver black screen and waiting for user inout during
playlist processing.
'''
import queue
import threading
import time
import os
import logging
from multiprocessing.connection import Client
import pickle
import json

from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.core.window import Window


from selectable_items import Select, SelectButton, SelectLabel, SelectLabelBg
import includes
from volume_widget import VolumeIndicator
from ipc import Ipc
from selectable_items import Select


class OsdController(Select):
    def enable(self, args):
        ipc = Ipc()
        logging.error("Thomas: osd controller enable function called")
        ipc.sendCmd('osdTop', 6002) #TODO: define port in config file

    def disable(self, args):
        ipc = Ipc()
        logging.error("Thomas: osd controller disable function called")
        ipc.sendCmd('osdBackground', 6002) #TODO: define port in config file


class MenuOSD(StackLayout, Select):
    '''On Screen Display (fixed height 50px (button height) + 5px (status border))'''
    btnPrevious = None
    btnNext = None
    btnPlay = None
    btnPaus = None
    btnStop = None
    volume = None
    colorIndicator = None
    id = None
    gap = None
    timeStep = 0.1
    thread = None
    idleCounter = 0
    #ena = True
    active = False
    ctrlQueue = None
    wId = 0
    enableDone = False
    widgets = []
    isSelectable = True
    osdCtrl = None


    #Empty functions for callbacks which need to be setup
    def onPlaylistEnter(self, args):
        '''callback that is executed when we press enter button while osd is active'''


    def playlistAbort(self, args):
        '''callback to stop current execution of media playback'''


    def playlistPrevious(self, args):
        '''callback to swicht to previous media file in playlist mode'''


    def playlistNext(self, args):
        '''callback to swicht to next media file in playlist mode'''



    def setColorIndicator(self, color):
        '''Set the color of the 5px high indicator border at the bottom of OSD'''
        self.colorIndicator.background_color = color

    onEnterPlay = None
    # def onEnterPlay(self, args):
    #     #'''These are the callback functions which are triggered when play button is pressed'''
    #     #logging.error("MenuOSD: onEnterPlay needs to be assigned to playlist callback!")
    #     pass

    def onEnterPause(self, args):
        '''Callback function which needs to be set by parent to execute pause fct of player'''
        logging.error("MenuOSD: onEnterPause needs to be assigned to playlist callback!")


    def onEnterPrevious(self, args):
        '''called when previous button on OSD is pressed'''
        self.playlistPrevious(None)

    def onEnterNext(self, args):
        '''called when next button on OSD is pressed'''
        self.playlistNext(None)

    def onEnterStop(self, args):
        '''This function is executed when we hit stop'''
        self.disable(None)
        self.playlistAbort(None)

    def _worker(self):
        logging.debug("MenuOSD: thread called...")

        while True:
            time.sleep(self.timeStep)
            self.idleCounter = self.idleCounter + self.timeStep

            if self.volume.muteState:
                continue

            #just limit the counter value
            if self.idleCounter > includes.config['settings']['osdTime'] and self.isVisible:
                self.idleCounter = includes.config['settings']['osdTime'] + 1
                self.wId = 0
                for wid in self.widgets:
                    wid.disable(None)

                self.isVisible = False
                self.osdCtrl.disable(None)


            if not self.ctrlQueue.empty():

                cmd = self.ctrlQueue.get()
                if cmd['cmd'] == 'resetCnt':
                    self.idleCounter = 0
                    self.isVisible = True


    def left(self, args):
        '''Logic to select next OSD element to the left from currently selected item'''

        if not self.isVisible:
            self.enable(None)
            self.wId = 0
            self.widgets[self.wId].enable(None)
            return

        self._resetCnt()

        if self.wId < len(self.widgets) and self.wId >= 0:
            if self.wId > 0:
                self.widgets[self.wId].disable(None)

            self.wId = includes.clipInt(self.wId - 1, min=0, max=4)
            self.widgets[self.wId].enable(None)

    def right(self, args):
        '''Logic to select next OSD element to the right from currently selected item'''
        if not self.isVisible:
            self.enable(None)
            self.wId = 0
            self.widgets[self.wId].enable(None)

            return

        self._resetCnt()

        if self.wId < len(self.widgets):
            self.widgets[self.wId].disable(None)

            self.wId = includes.clipInt(self.wId + 1, min=0, max=4)
            self.widgets[self.wId].enable(None)

    def _resetCnt(self):
        self.ctrlQueue.put({'cmd':'resetCnt'})


    def enable(self, args):
        self._resetCnt()
        return

    def disable(self, args):
        self.ctrlQueue.put({'cmd':'invisible'})


    def enter(self, args):
        '''
            If OSD is visible enter will activate button press, otherwise
            enter will be forwarded to playlist controller
        '''
        if self.isVisible:
            self.widgets[self.wId].onEnter(args)
        else:
            #when OSD is not active, enter button will be forwareded to the player
            #this is used to switch to the next media file in playlist mode
            if self.onPlaylistEnter is not None:
                self.onPlaylistEnter(None)



    def changeSize(self, widget, value):
        '''resize the child attributes if widht or height changes'''
        winCenter = int(Window.width / 2)
        winBoundaryLeft = winCenter - int(self.runtime.width / 2)
        winBoundaryRight = winCenter + int(self.runtime.width / 2)

        self.gap0.width = winBoundaryLeft-(5*50)
        self.gap.width = Window.width-winBoundaryRight-60

    def volumeUp(self, args):
        '''Increase the audio volume'''
        self._resetCnt()
        self.volume.volumeUp()

    def volumeDown(self, args):
        '''Decrease the audio volume'''
        self._resetCnt()
        self.volume.volumeDown()

    def muteToggle(self, args):
        '''Mute/unmute the audio'''
        self._resetCnt()
        self.volume.muteToggle()

    def _addAllWidgets(self):
        '''Add all widgets to the OSD and hide them with opacity = 0'''
        self.widgets.append(self.btnPause)
        self.widgets.append(self.btnPlay)
        self.widgets.append(self.btnStop)
        self.widgets.append(self.btnPrevious)
        self.widgets.append(self.btnNext)

        for wid in self.widgets:
             self.add_widget(wid)


        self.add_widget(self.gap0)
        self.add_widget(self.runtime)
        self.add_widget(self.gap)
        self.add_widget(self.volume)

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id', None)

        if self.id is None:
            logging.error("MenuOSD: id not defined...")
            return

        self.id = int(self.id)

        super(MenuOSD, self).__init__()

        self.btnPrevious = SelectButton(
            imgPath="atlas://resources/img/pi-player/previous",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(3)
        )

        self.btnNext = SelectButton(
            imgPath="atlas://resources/img/pi-player/next",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(0)
        )

        self.btnPlay = SelectButton(
            imgPath="atlas://resources/img/pi-player/play",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(1),

        )


        self.btnPause = SelectButton(
            imgPath="atlas://resources/img/pi-player/pause",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(2)
        )

        self.btnStop = SelectButton(
            imgPath="atlas://resources/img/pi-player/stop",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(3)
        )


        self.runtime = SelectLabel(
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=200,
            id=str(3),
            text="00:00:23"
        )

        winCenter = int(Window.width / 2)
        winBoundaryLeft = winCenter - int(self.runtime.width / 2)
        winBoundaryRight = winCenter + int(self.runtime.width / 2)


        self.gap0 = Label(
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=winBoundaryLeft-(5*50),
            #background_color=(1,0,1,0.5)
        )

        self.gap = Label(
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            #background_color=(0,1,1,0.5),
            width=Window.width-winBoundaryRight-60
        )


        self.volume = VolumeIndicator(
            incVal=1,
            size_hint=(None, None),
            width=50,
            height=50,
            radius=15,
            bgColor=includes.colors['gray'],
            color=includes.colors['oldblue'],
            value=0,
            mode='line'
        )

        self._addAllWidgets()

        #add a colored 5px indicator bar at the bottom of the OSD to show status
        self.colorIndicator = SelectLabelBg(
            # height=50,#includes.styles['pListIndiactorHeight'],
            # size_hint_y=None,
            size_hint_x=None,
            width=Window.width,
            background_color=includes.colors['black'],
            id="-1",
            text=""
        )

        self.add_widget(self.colorIndicator)

        self.height = 50 + 5
        self.size_hint_y = None

        self.bind(size=self.changeSize)
        self.isVisible = False

        #Thread and queue handling
        self.ctrlQueue = queue.Queue()
        self.thread = threading.Thread(target=self._worker)
        self.thread.setDaemon(True)
        self.thread.start()

        self.wId = 0
        self.osdCtrl = OsdController()



#-------------------
#
from key_handler import KeyHandler
class OSDMain(App):
    def onPress(self, args):
        scancode = args[1]
        logging.error("dfgdghdfghdghdf: {}".format(scancode))
        if scancode == 'left':
            self.osd.left(None)
        elif scancode == 'right':
            self.osd.right(None)
        elif scancode == '+':
            self.osd.volumeUp(None)
        elif scancode == '-':
            self.osd.volumeDown(None)
        elif scancode == 'm':
            self.osd.muteToggle(None)

    '''This is just a Kivy app for testing the OSD on its own - do not rely on this!'''
    def build(self):
        self.osd = MenuOSD(id="0")
        return self.osd

if __name__ == "__main__":
    handler = KeyHandler()

    main = OSDMain()
    handler.onPress = main.onPress
    #Window.size = (Window.width, 50)
    main.run()
