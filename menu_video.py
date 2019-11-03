import logging
import os

import includes
from selectable_items import SelectListView

class FileList(SelectListView):
    rootdir = ""
    dirTree = []
    supportedTypes = None
    screenmanager = None
    playerProcess = None
    topTextVisible = False

    def delTopText(self):
        if not self.topTextVisible:
            return

        super(FileList, self).delTopText()
        self.topTextVisible = False

    def addTopText(self, text, user):
        super(FileList, self).addTopText(text, user, includes.styles['warning'])

    def resize(self, widget, value):
        pass

    def _onEnterPlayer(self, args):
        pass

    def enter(self, args):
        path = self.rootdir

        for item in self.dirTree:
            tmp = item[0]
            path = os.path.join(path, tmp)

        path = os.path.join(path, self.widgets[self.wId].text)

        if self.widgets[self.wId].text == "...": #jump to previous directory
            tmp = self.dirTree.pop(len(self.dirTree)-1)
            path = self.rootdir

            for item in self.dirTree:
                path = os.path.join(path, item[0])

            self.layout.clear_widgets()
            self.widgets = []

            isSubdir = len(self.dirTree) > 0
            self._addFile(path, isSubdir, tmp[1])
            self.widgets[self.wId].enable(None)

        elif os.path.isfile(path): #We hit enter on a video file so play it
            if args is None:
                args = {}

            args['path'] = path

            if self.widgets[self.wId].user:
                for item in self.widgets[self.wId].user:
                    args[item] = self.widgets[self.wId].user[item]

            self._onEnterPlayer(args)

            if 'isRerun' in args:
                if args['isRerun']:
                    self.delTopText()

        elif os.path.isdir(path):
            self.layout.clear_widgets()

            self.dirTree.append((self.widgets[self.wId].text, self.wId))
            self.widgets = []
            self._addFile(path, True, None)

            if len(self.widgets) > 0:
                self.widgets[0].enable(None)

    def _addFile(self, path, isSubdir, wId):

        if isSubdir and self.showDirs:
            self.add("...", True)

        files = os.listdir(path)
        files.sort()

        dirs = []
        docs = []
        for item in files:
            tmpPath = os.path.join(path, item)
            if os.path.isdir(tmpPath):
                dirs.append(item)
            else:
                docs.append(item)

        #add all directories first
        for item in dirs:
            self.add(item.strip(), isDir=True)

        #then add all the files
        for item in docs:
            if item.lower().endswith(self.supportedTypes):
                self.add(item.strip(), False)

        if len(self.widgets) > 0:
            if wId:
                self.wId = wId

                self.scroll_to(self.widgets[self.wId], animate=False)
            else:
                self.wId = 0

            if self.selectFirst or isSubdir:
                self.widgets[self.wId].enable(None)

        if includes.db['runtime'] > 0 and self.type == "video":
            user = {'tSeek':includes.db['runtime'], 'isRerun':True}
            self.addTopText(includes.db['mediaPath'], user)

    def __init__(self, **kwargs):
        if 'rootdir' not in kwargs:
            logging.error("MenuVideo: root dir not give as parameter")
            return

        if not os.path.exists(kwargs['rootdir']):
            logging.error("MenuVideo: root dir does not exist")
            return

        self.rootdir = kwargs.pop('rootdir')

        if 'selectFirst' in kwargs:
            self.selectFirst = kwargs['selectFirst']

        else:
            self.selectFirst = True

        self.showDirs = True
        if 'showDirs' in kwargs:
            self.showDirs = kwargs['showDirs']

        self.supportedTypes = kwargs.pop('supportedTypes', None)
        if not self.supportedTypes:
            logging.error("MenuVideo: supported files types for video player not set")
            return

        self.supportedTypes = tuple(self.supportedTypes.split(','))
        self.screenmanager = kwargs.pop('screenmanager', None)
        self.type = kwargs.pop('type', "unknown")

        if not self.screenmanager:
            logging.error("MenuVideo: screenmanager not set")
            return

        super(FileList, self).__init__(**kwargs)

        self.widgets = []
        self._addFile(self.rootdir, False, None)
        self.wId = -1
        self.bind(width=self.resize)
