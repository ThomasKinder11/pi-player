from isha_pi_kivy import *
import logging
import os, sys, time
from subprocess import threading
from globals import player

class MenuVideo(SelectListView):
    widget = None
    rootdir = ""
    dirTree = []
    supportedTypes = None# ('.mp4')
    screenmanager = None
    playerProcess = None
    running = False

    def __waitForPlayerEnd(self):
        while player.process.poll() == None:
            time.sleep(1)


        self.screenmanager.current = "main_menu"
        self.running = False

    def enter(self):
        path = self.rootdir

        for item in self.dirTree:
            path = os.path.join(path, item[0])

        path = os.path.join(path, self.widgets[self.wId].text)

        if self.widgets[self.wId].text == "...":
            tmp = self.dirTree.pop(len(self.dirTree)-1)
            path = self.rootdir

            for item in self.dirTree:
                path = os.path.join(path, item[0])

            self.layout.clear_widgets()
            self.widgets = []

            isSubdir = len(self.dirTree) > 0
            self._addFile(path, isSubdir, tmp[1])

        elif os.path.isfile(path): #We hit enter on a video file so play it

            self.screenmanager.current = "osd" #TODO: Switch to black screen
            self.running = True
            player.play(path)
            time.sleep(1)

            self.playerProcess = threading.Thread(target = self.__waitForPlayerEnd)
            self.playerProcess.start()

        elif os.path.isdir(path):
            self.layout.clear_widgets()

            self.dirTree.append((self.widgets[self.wId].text, self.wId))
            self.widgets = []
            self._addFile(path, True, None)

    def _addFile(self, path, isSubdir, wId):

        if isSubdir:
            self.add("...")

        files = os.listdir(path)
        for item in files:
            tmpPath = os.path.join(path, item)

            if os.path.isdir(tmpPath) or item.lower().endswith(self.supportedTypes):
                self.add(item.strip())


        if len(self.widgets) > 0:
            if wId:
                self.wId = wId
                self.scroll_to(self.widgets[self.wId], animate=False)
            else:
                self.wId = 0

            self.widgets[self.wId].enable()

    def __init__(self, **kwargs):
        if not 'rootdir' in kwargs:
            logging.error("MenuVideo: root dir not give as parameter")
            return

        if not os.path.exists(kwargs['rootdir']):
            logging.error("MenuVideo: root dir does not exist")
            return

        self.rootdir = kwargs.pop('rootdir')

        self.supportedTypes = kwargs.pop('supportedTypes', None)
        if not self.supportedTypes:
            logging.error("MenuVideo: supported files types for video player not set")
            return

        self.screenmanager = kwargs.pop('screenmanager', None)

        if not self.screenmanager:
            logging.error("MenuVideo: screenmanager not set")
            return

        super(MenuVideo, self).__init__(**kwargs)

        self._addFile(self.rootdir, False, None)
