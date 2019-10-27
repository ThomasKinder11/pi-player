from isha_pi_kivy import *
from select_listview import *
import logging
import globals
from volume_widget import VolumeIndicator
import queue
import threading
import time
import os


from kivy.uix.stacklayout import StackLayout
from kivy.app import App
from kivy.core.window import Window

class MenuOSD(StackLayout, Select):
    btnPrevious = None
    btnNext = None
    btnPlay = None
    btnPaus = None
    btnStop = None
    volume = None
    id = None
    gap = None
    timeStep = 0.0091
    thread = None
    idleCounter = 0
    #ena = True
    active = False
    ctrlQueue = None
    wId = 0
    enableDone = False
    widgets = []
    isSelectable = True

    """
    These are the callback functions which are triggered when a button on the OSD
    is activated. Here we can implemente the player control.
    """
    def _onEnterPlay(self):
        logging.error("MenuOSD: _onEnterPlay")
        if os.name == "posix":
            logging.error("MenuOSD: for linux _onEnterPlay")
            cmd = 'echo \'{ "command": ["set_property", "pause", false] }\''
            cmd = cmd + "| sudo socat - " + globals.config[os.name]['tmpdir'] + "/socket"
            #logging.error("MenuOSD: for linux _onEnterPlay cmd = {}".format(cmd))
            ret = os.system(cmd)
            logging.error("MenuOSD: executed os.system call... {}".format(ret))

    def _onEnterPause(self):
        logging.error("MenuOSD: _onEnterPause")
        if os.name == "posix":
            cmd = 'echo \'{ "command": ["set_property", "pause", true] }\''
            cmd = cmd + "| sudo socat - " + globals.config[os.name]['tmpdir'] + "/socket"
            #os.system('echo \'{ "command": ["set_property", "pause", true] }\' | sudo socat - /home/thomas/tmp/socket')
            os.system(cmd)

    def _onEnterPrevious(self):
        logging.error("MenuOSD: _onEnterPrevious")


    def _onEnterNext(self):
        logging.error("MenuOSD: _onEnterNext")

    def _onEnterStop(self):
        logging.error("MenuOSD: _onEnterStop")
        if os.name == "posix":
            #os.system('echo \'{ "command": ["quit"] }\' | sudo socat - ~/tmp/socket')
            cmd = 'echo \'{ "command": ["quit"] }\''
            cmd = cmd + "| sudo socat - " + globals.config[os.name]['tmpdir'] + "/socket"
            os.system(cmd)
            # os.system('echo \'{ "command": ["quit"] }\' | sudo socat - ~/tmp/socket')


    def _worker(self):
        logging.debug("MenuOSD: thread called...")

        while True:
            #logging.debug("MenuOSD: alive...")
            time.sleep(self.timeStep)
            self.idleCounter = self.idleCounter + self.timeStep

            #just limit the counter value
            if self.idleCounter > globals.config['settings']['osdTime']:
                self.idleCounter = globals.config['settings']['osdTime']
                self.wId = 0
                for wid in self.widgets:
                    wid.opacity = 0
                    wid.disable(None)
                self.runtime.opacity = 0


            if not self.ctrlQueue.empty():

                cmd = self.ctrlQueue.get()

                if cmd['cmd'] == 'visible':
                    self.idleCounter = 0
                    logging.debug("MenuOSD: queue command has been received visible")

                    for wid in self.widgets:
                        wid.opacity = 1.0

                    self.runtime.opacity = 1.0

                    self.enableDone = True


    def left(self, args):
        logging.debug("MenuOSD: left function called [wid = {}]".format(self.wId))
        self.enable(None)

        if self.wId <= len(self.widgets) and self.wId > 1:
            self.widgets[self.wId-1].disable(None)

            if self.wId >= 2:
                self.widgets[self.wId - 2].enable(None)

                self.wId = self.wId - 1

    def right(self, args):
        logging.debug("MenuOSD: right function called [wid = {}]".format(self.wId))
        self.enable(None)

        if self.wId < len(self.widgets):
            self.widgets[self.wId].enable(None)

            if self.wId >= 1:
                self.widgets[self.wId - 1].disable(None)

            self.wId = self.wId + 1


    def enable(self, args):
        #logging.debug("MenuOSD: enable function called")
        self.enableDone = False
        self.ctrlQueue.put({'cmd':'visible'})
         #always start OSD on first button

        while not self.enableDone:
            time.sleep(0.25)

        return


    def disable(self, args):
        pass#self.ctrlQueue.put({'cmd':'hide'})

    def enter(self, args):
        self.widgets[self.wId-1].onEnter()

    def changeSize(self, widget, value):
        winCenter= int(Window.width / 2)
        winBoundaryLeft = winCenter - int(self.runtime.width / 2)
        winBoundaryRight = winCenter + int(self.runtime.width / 2)

        self.gap0.width = winBoundaryLeft-(5*50)
        self.gap.width = Window.width-winBoundaryRight-60

    def volumeUp(self):
        self.volume.volumeUp()

    def volumeDown(self):
        self.volume.volumeDown()

    def muteToggle(self):
        self.volume.muteToggle()

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id', None)

        if self.id == None:
            logging.error("MenuOSD: id not defined...")
            return

        self.id = int(self.id)

        super(MenuOSD, self).__init__()

        self.btnPrevious = SelectButton(
            imgPath= "./resources/img/previous",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(3)
        )

        self.btnNext = SelectButton(
            imgPath= "./resources/img/next",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(0)
        )

        self.btnPlay = SelectButton(
            imgPath= "./resources/img/play",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(1),

        )


        self.btnPause = SelectButton(
            imgPath= "./resources/img/pause",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(2)
        )

        self.btnStop = SelectButton(
            imgPath= "./resources/img/stop",
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

        winCenter= int(Window.width / 2)
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
            bgColor=(0.4,0.4,0.4,1),
            color=(0, 0, 1, 0.5),
            value=0
        )

        self.btnPlay.onEnter = self._onEnterPlay
        self.btnPause.onEnter = self._onEnterPause
        self.btnStop.onEnter = self._onEnterStop
        self.btnNext.onEnter = self._onEnterNext
        self.btnPrevious.onEnter = self._onEnterPrevious

        self.widgets.append(self.btnPause)
        self.widgets.append(self.btnPlay)
        self.widgets.append(self.btnStop)
        self.widgets.append(self.btnPrevious)
        self.widgets.append(self.btnNext)


        for wid in self.widgets:
            self.add_widget(wid)
            wid.opacity = 0

        self.runtime.opacity = 0

        self.add_widget(self.gap0)
        self.add_widget(self.runtime)
        self.add_widget(self.gap)
        self.add_widget(self.volume)

        #self.gap.width = Window.width - 10
        self.height = 50
        self.size_hint_y = None
        #self.orientation = 'rl-tb'

        self.bind(size=self.changeSize)

        self.ctrlQueue= queue.Queue()
        self.thread = threading.Thread(target=self._worker)
        self.thread.setDaemon(True)
        self.thread.start()




class OSDMain(App):
    def build(self):
        return MenuOSD(id="0")

if __name__ == "__main__":
    #Window.size = (Window.width, 50)
    OSDMain().run()
