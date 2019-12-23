import logging
import os

import includes
from selectable_items import SelectListView

class FileList(SelectListView):
    rootdir = ""
    dirTree = []
    supportedTypes = None
    #screenmanager = None
    playerProcess = None
    topTextVisible = False

    # def resize(self, widget, value):
    #     #self.size = value
    #     logging.error("thomas: resize called")
    #     pass

    # def position(self, widget, value):
    #     self.pos = value

    def _onEnterPlayer(self, args):
        pass

    def back(self, args):
        logging.error("BrowserBack: called")
        if len(self.dirTree) >= 1:
            tmp = self.dirTree.pop(len(self.dirTree)-1)
            path = self._getCurPath()

            self.layout.clear_widgets()
            self.widgets = []

            isSubdir = len(self.dirTree) > 0
            self._addFile(path, isSubdir, 0)
            self.widgets[self.wId].enable(None) #TODO: should we not alwys enable the wId = 0? Is this line actually needed?
            return False
        else:
            return True

    def home(self, args):
        if len(self.dirTree) == 0:
            return True

        self.dirTree = []
        self.layout.clear_widgets()
        self.widgets = []
        self._addFile(self.rootdir, False, 0)

        return False

    def _getCurPath(self):
        logging.error("thomas: dirtree = {}".format(self.dirTree))
        path = self.rootdir

        for item in self.dirTree:
            tmp = item[0]
            path = os.path.join(path, tmp)


        return path


    def enter(self, args):
        logging.error("Thomas: enter pressed")
        path = self._getCurPath()
        logging.error("Thomas: path = {}".format(path))

        path = os.path.join(path, self.widgets[self.wId].text)
        logging.error("Thomas: path = {}".format(path))


        if self.widgets[self.wId].text == "...": #jump to previous directory
            logging.error("Thomas: in ...")
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
            logging.error("Thomas: is file")
            if args is None:
                args = {}

            args['path'] = path
            args['supportedTypes'] = self.supportedTypes

            if self.type == 'video' and includes.config['video']['autoplay'] == 'true':
                args['autoplay'] = True
            elif self.type == 'music' and  includes.config['audio']['autoplay'] == 'true':
                args['autoplay'] = True
            else:
                args['autoplay'] = False

            logging.debug("MenuVideo: called enter on audi mFile with args = {}".format(args))
            self._onEnterPlayer(args)


        elif os.path.isdir(path):
            logging.error("Thomas: isdir type={}".format(self.type))
            self.layout.clear_widgets()

            self.dirTree.append((self.widgets[self.wId].text, self.wId))
            self.widgets = []
            self._addFile(path, True, None)

            if len(self.widgets) > 0:
                self.widgets[0].enable(None)

        logging.error("Thomas: type={}".format(self.type))

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
            else:#in case wId is lower then zero which can happen
                self.wId = 0

            self.scroll_to(self.widgets[self.wId], animate=False)
            #self.widgets[self.wId].enable(None) #TODO: should we not alwys enable the wId = 0? Is this line actually needed?


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
        #self.screenmanager = kwargs.pop('screenmanager', None)
        self.type = kwargs.pop('type', "unknown")
        self.autoplay = kwargs.pop('Autoplay', False)

        # if not self.screenmanager:
        #     logging.error("MenuVideo: screenmanager not set")
        #     return

        super(FileList, self).__init__(**kwargs)

        self.widgets = []
        self._addFile(self.rootdir, False, None)
        self.wId = -1
        #self.bind(width=self.resize)
        #self.bind(size=self.resize)




if __name__ == "__main__":
    from menu_video import FileList
    from kivy.core.window import Window
    from kivy.app import App



    class Main(App):
        def testFunc(self):
            import time
            time.sleep(2)

            #Select first element which should be a directory
            self.fList.enable(None)
            time.sleep(1)

            for i in range(55):
                self.fList.enable(None)
                time.sleep(0.1)

            return

            for k in range(3):
                for i in range(2):

                    #enter in that directory
                    self.fList.enter(None)
                    time.sleep(1)

                    #select in the second sub dir
                    self.fList.enable(None)
                    time.sleep(1)

                    #enter in second sub dir
                    self.fList.enter(None)
                    time.sleep(1)

                    #go up one directory
                    self.fList.browserBack(None)
                    time.sleep(1)

                    #go up one directory
                    self.fList.browserBack(None)
                    time.sleep(1)

                #enter in that directory
                self.fList.enter(None)
                time.sleep(1)

                #select in the second sub dir
                self.fList.enable(None)
                time.sleep(1)

                #enter in second sub dir
                self.fList.enter(None)
                time.sleep(1)

                #go back to root
                self.fList.home(None)
                time.sleep(1)



        def build(self):
            self.fList = FileList(
                id="0",
                rootdir="/mnt/Ishamedia/",
                enaColor=includes.styles['enaColor0'],
                bar_width=10,
                #size_hint_x=(1, 1),
                #size=(Window.width, Window.height),
                supportedTypes="mp3,mp4,txt",
                selectFirst=False,
                type="video"
            )

            from  subprocess import threading

            workThread = threading.Thread(target=self.testFunc)
            workThread.setDaemon(True)
            workThread.start()

            from kivy.uix.stacklayout import StackLayout

            lay = StackLayout()
            lay.add_widget(self.fList)
            return lay

            return self.fList





    Main().run()
