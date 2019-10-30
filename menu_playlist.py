import includes
from kivy.app import App
import kivy
from kivy.utils import get_color_from_hex as hexColor
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from selectable_items import *
from menu_video import *
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color, Line
from  subprocess import Popen, threading
import queue
import time

def createPlayListEntry(path, name, id, start):
    tmp = {
        int(id):{
            'path': path,
            'name': name,
            'pre' : "",
            'post' : "",
            'start' : 0,
            'end' : 0
        }
    }
    # tmp['path'] = path
    # tmp['name'] = name
    # tmp['pre'] = ""
    # tmp['post'] = ""
    return tmp


class MenuPlaylist(StackLayout, Select):
    _FILE_LIST = 0
    _JSON_LIST = 1
    mode = _FILE_LIST # mode 0 = json file fiew is selected, mode = 1 the list view of files in json are selected
    select = "json"
    pList = None
    workThread = None
    ctrlQueue = None
    osdEnable = None #callback function to enable osd
    osdDisable = None #callback function to disable osd
    osdColorIndicator = None
    hasNext = False
    hasPrevious = False

    def hasNextTrack(self):
        return self.hasNext

    def hasPreviousTrack(self):
        return self.hasPrevious

    def isPaused(self):
        return not includes.player.isPlaying

    def isPlaying(self):
        return includes.player.isPlaying

    def pause(self, args):
        includes.player.pause(args)

    def enable(self, args):#down
        if self.mode == self._FILE_LIST  and len(self.fileList.widgets) > 0:
            logging.info("enable/down")

            id = self.fileList.wId + 1

            if id == len(self.fileList.widgets):
                id = id - 1

            self.updateJsonFiles(self.fileList.widgets[id].text)
            ret = self.fileList.enable(None)

            return ret

        elif self.mode == self._JSON_LIST:


            self.files.enable(None)
            return False

    def disable(self,args):#up

        if self.mode == self._FILE_LIST and len(self.fileList.widgets) > 0:
            logging.info("disable/up")

            id = self.fileList.wId - 1
            if id < 0:
                id = 0


            self.updateJsonFiles(self.fileList.widgets[id].text)

            return self.fileList.disable(None)

        elif self.mode == self._JSON_LIST:
            self.files.disable({'disTop':False})
            return False

    def disableAll(self, args):
        for wid in self.fileList.widgets:
            wid.disable(None)


    def left(self, args):
        logging.debug("MenuPlayList: left called...")

        if self.mode == self._FILE_LIST:

            return True
        elif self.mode == self._JSON_LIST:
            self.mode = self._FILE_LIST

            for wid in self.files.widgets:
                wid.disable({'inc':False})
            self.files.wId = -1

            #self.fileList.enaColor = (1,0,0,1)
            tmpID = self.fileList.wId
            self.fileList.widgets[tmpID].label.color = self.fileList.enaColor
        pass

    def right(self,args):
        logging.info("right")
        if args != None:
            enableFilesView = args.pop('enableFilesView', True)
        else:
            enableFilesView = True
        #self.fileList.widgets[0].enaColor = [1,0,0,1]
        if self.mode == self._FILE_LIST and len(self.fileList.widgets) > 0:
            self.mode = self._JSON_LIST

            if enableFilesView:
                self.files.enable(None)

            tmpID = self.fileList.wId
            self.fileList.widgets[tmpID].label.color = [1,0.5,0.2,1]
        elif self.mode == self._JSON_LIST:
            pass

    def _validateJson(self,path):
        #check if number of eldn to the nodes, id must
        #accour in sequence without any gaps in between
        for i in range(len(self.pList)):
            #msg = "PlayList:  id = {} / str(id) ={} / plist = {}\n".format(i, str(i), self.pList)
            #logging.error(msg)
            if not (str(i) in self.pList):
                msg = "PlayList: playlist file ids not correct, stopped at id = {}\n".format(i)
                msg = msg + "\tplist = {} / i = {} \n".format(self.pList, i)
                msg = msg + "\tpath = {}".format(path)
                logging.error(msg)

                return -1

        i = 0
        for item in self.pList:
            if item != str(i):
                msg = "PlayList: playlist ids not in sequential order !\n"
                msg = msg + "\tpath = {}\n".format(path)
                msg = msg + "\tlist = {}\n".format(self.pList)
                msg = msg + "\t i = {}\n".format(i)
                logging.error(msg)
                return -2
            i = i + 1

        return 0


    def updateJsonFiles(self, text):
        path = os.path.join(includes.config[os.name]['playlist']['rootdir'], text)

        if os.path.isdir(path):
            return

        with open(path) as playFile:
            self.pList = json.load(playFile)

        if self._validateJson(path) < 0:
            logging.error("MenuPlaylist: the Json file for selected playlist is not correct")
            return

        self.files.layout.clear_widgets()
        self.files.wId = -1
        self.files.widgets = []


        for item in self.pList:
            logging.error("??????????????????: itm ;; {}".format(self.pList[item]['name']))
            self.files.add(self.pList[item]['name'], False)

        logging.error("??????????????????: number widget = {}".format(len(self.files.widgets)))


    '''
    This method will process when we press the enter key on the selected playlist.
    If we also have a specific file from the playlist selected we start playing
    from that file. This function will ensure that the last played element in
    the playlist is highlighted so that after a video is stopped we can continue
    from the same position. This function shoudl be triggered when the
    enter button is pressed while the playlist menu is active.


    The playlist is a json file which will be read with updateJsonFiles() when
    a playlist is selected. This will save the content of the playlist in a
    dictonary self.pList.

    The json file has multiple entries, where each entry starts with a id and
    then the content. The id specifies the order in which the files are being
    added to the playlist

    --> TODO: we need to change updateJsonFiles() function
    to parse the ids and rearanges them so we list them in the correct order
    independent in which order they are listed in the json file.


    The follwing example shows a playlist with a single entry, all
    paramters are case sensitive.

    {
      id:{
        "path":"mypath",
        "name": "muckel.wav",
        "post":"execute this before playback",
        "pre": "execute this after playback",
        "start":0,
        "end":0,
        "type":"audio"
      }
     }

    id:    this is an integer value defining the order in which files in playlist
            are played. It should be incremented sequentially without any gap in between
            The python app will check this and will not load the files of the json file

    path:   this is the absolute path to the media file
    name:   this is the name of the file, which will be displayed in the GUI
    pre:    here we can define a set of commands that shall be executed before a
            video starts.
                - BLACKSCREEN: will start the video on black screen, waiting for
                             for the user to press the 'enter/ok' button to start
                            playback
    post:   here we can define a set of commands that shall be executed after a
            video is played completely.
                - BLACKSCREEN: stop video on black screen,
                - PLAYNEXT: automatically plays the next file
    start: start the video from a specified time value in seconds. (not implemented yet)
    stop:  stop the video at the specified time in seconds         (not implemented yet)

    '''
    def _waitForCmd(self, key, value):
        while True:
            logging.debug("_waitForCmd: wait for cmd...")
            while self.ctrlQueue.empty():
                time.sleep(0.25)
                continue

            cmd = self.ctrlQueue.get()
            logging.debug("_waitForCmd: got cmd = {}...".format(cmd))
            cmd = cmd['cmd']

            if 'abort' in cmd:
                return ('abort')

            if 'previous' in cmd:
                return ('previous')

            if 'next' in cmd:
                return ('next')


            if value != None:
                if key in cmd:
                    logging.debug("key is in cmd")
                    if cmd[key] == value:
                        logging.debug("key value match cmd")
                        return ('match', True)
            else:
                logging.debug("_waitForCmd: return the received cmd = {}".format(cmd))
                return ('cmd', cmd)

    prevTimestamp = None
    def _previousNextContrl(self, mode, cmd, index, plistStart, isPre):
        doubleClickPrev = False
        skipFirst = False

        if 'previous' in cmd:
            logging.error("ßßßßßßßßßßßßßß: time = {} / previos = {} / div = {}".format(time.time(), self.prevTimestamp, time.time() - self.prevTimestamp))
            if time.time() - self.prevTimestamp <= 3: #we have 3 seconds to skip to previous
                self.prevTimestamp = time.time()
                doubleClickPrev = True
                logging.error("ßßßßßßßßßßßßßßßßßßßßßßßßßßß: double previous")

            self.prevTimestamp = time.time()

            if isPre or doubleClickPrev: #if media files has been playing for more then 10s
                doubleClickPrev = False

                if index >= 1:
                        index = index - 1
                        self.files.disable(None)
                else:
                    index = 0
                    plistStart = 0

                plistStart = index #Todo: Is this correct ? ::TK:: it should start on indes isnt it?

            #else: return value as they are nothing to do

            if mode == "json":

                skipFirst = True

            return (True, index, plistStart, skipFirst)

        elif 'next' in cmd: #TODO: do we need to do soemething here?  ::TK::
            pass

        #If nothing happens return original values
        return (False, index, plistStart, False)


    def _playListControl(self, playlist, plistStart, skipFirst, mode):
        i = 0
        skipPre = False

        while i < len(playlist):
            item = list(playlist.keys())[i]
            logging.info("############## item = {} / i = {}".format(item, i))
        #for item in playlist:

            if int(item) < plistStart:
                i = i + 1
                continue

            #mark if there is a file before this
            if i > 0:
                self.hasPrevious = True
            else:
                self.hasPrevious = False

            #mark if there is a file after this
            if i < len(playlist) - 1:
                self.hasNext = True
            else:
                self.hasNext = False



            if not skipFirst:
                if mode == "json":
                    self.files.enable(None)

            if 'pre' in playlist[item] and skipPre == False:
                logging.debug("ßßßßßßßßßßß Pre is defined = {}".format(playlist[item]['pre']))

                if 'BLACKSCREEN' ==  playlist[item]['pre']:
                    logging.debug("pre black wait..")
                    self.osdColorIndicator('red')

                    ret = self._waitForCmd('key', 'enter') #blocks until button has been pressed #TODO this is not working
                    logging.debug("pre black after wait. ret value = {}".format(ret))
                    self.osdColorIndicator('black')
                    if 'abort' in ret:
                        logging.info("Abort in pre black screen...")
                        return

                    logging.info("New handler function prev /next...")

                    stat, i, plistStart, skipFirst =  self._previousNextContrl(mode, ret, i, plistStart, True)
                    if stat == True:
                        logging.info("ßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßß Stat was true...")
                        skipPre = True
                        continue
            skipPre = False
            #
            # Play the mdia file with the player
            #
            if 'start' in playlist[item]:
                tSeek = playlist[item]['start']
            else:
                tSeek = 0

            includes.player.play(playlist[item]['path'], tSeek)

            ret = self._waitForCmd('event', 'end') #blocks until  we got signal that playback is finished
            if 'abort' in ret:
                if includes.player.process:
                    includes.player.process.kill()
                logging.info("Abort/ during playback...")
                return
            else:
                stat, i, plistStart, skipFirst =  self._previousNextContrl(mode, ret, i, plistStart, False)
                if includes.player.process:
                    includes.player.process.kill()

                logging.info("Next/Previous during playback...")

                if stat == True:
                    logging.info("Stat was true...")
                    skipPre = True
                    continue

            # stat, i, plistStart, skipFirst =  self._previousNextContrl(mode, ret, i, plistStart)
            # if stat:
            #     continue


            if 'post' in playlist[item]:
                logging.debug("$$ post is defined... post =  {}".format(playlist[item]['post']))
                #TODO: do we need to implement post black screen? is that needed?
                if 'PLAYNEXT' in playlist[item]['post']: #just start processing the next entry of the playlist : NOTICE: the next element should not have BLACKSCRREN define in pre
                    i = i + 1
                    continue

            i = i + 1

    def _processPlaylist(self):
        skipFirst = False
        while True:
            time.sleep(0.25)
            logging.error("_processPlaylist: wait for command")
            cmd = self._waitForCmd(None, None)
            if 'cmd' == cmd[0]:
                cmd = cmd[1]
            else:
                logging.error("MenuPlayList._processPlaylist: command error [1]...")
                return

            #only when mode is defined its something we can process otherwise wait for next command
            if not 'mode' in cmd:
                continue

            logging.debug("_processPlaylist:received command {}..".format(cmd))
            self.osdEnable(None)

            if cmd['mode'] == "json": #started via file list viewer for PlayList
                logging.debug("_processPlaylist: mode = json")
                if self.mode == self._FILE_LIST:
                    if len(self.fileList.children) > 0:
                        self.pListStartId = 0
                        text = self.fileList.widgets[self.fileList.wId].text
                        self.updateJsonFiles(text)
                        self.right({'enableFilesView':False})
                        skipFirst = False
                elif self.mode == self._JSON_LIST:
                    skipFirst = True
                    self.pListStartId = self.files.wId
                else:
                    continue

                playlist = self.pList
                plistStart = self.pListStartId
            elif cmd['mode'] == "virtual": #this is a virtual playlist not based on an actualy json file
                if 'playlist' in cmd:
                    logging.debug("ßßßßßßßßßßßßß: start virtual file...")
                    playlist = cmd['playlist']
                    plistStart = 0

                    logging.debug("ßßßßßßßßßßßßß: playlist = {}".format(playlist))



            includes.screenSaver.disable()

            self._playListControl(playlist, plistStart, skipFirst, cmd['mode'])


            self.osdDisable(None)
            includes.screenSaver.start(None)
            #self.screenmanager.current="main_menu"


    def abort(self, args):
        self.ctrlQueue.put(
        {
            'cmd':{
                'abort':None,
            }
        })

    def next(self, args):
        logging.debug("ßßßßßßß: Next called...")
        self.ctrlQueue.put(
        {
            'cmd':{
                'next':None,
            }
        })

    def previous(self, args):
        self.ctrlQueue.put(
        {
            'cmd':{
                'previous':None,
            }
        })

    def onPlayerEnd(self, args):
        self.ctrlQueue.put(
        {
            'cmd':{
                'event':'end',
            }
        })

    def startVirtualSingle(self,args):
        path = args.pop('path', None)
        start = args.pop('start', 0)

        if path == None:
            logging.error("startVirtualSingle: path was not specified in arguments!...")
            return

        tmp = createPlayListEntry(path, "VPL", 0, 0)

        cmd = {
            'cmd':{
                'playlist': tmp,
                'mode': 'virtual'
            }
        }

        self.ctrlQueue.put(cmd)

    def enter(self, args):
        if args != None:
            mode = args.pop('mode', "json")
        else:
            mode = "json"

        logging.debug("PlayList_Enter: enter callback executed...")
        #Do not execute this if we do not wait to recive a command
        # if includes.player.isPlaying:
        #     return

        self.ctrlQueue.put(
            {
                'cmd':{
                    'mode':mode,
                    'key':'enter',
                }
            }
        )


    def __init__(self, **kwargs):
        self.id = kwargs.pop('id', None)
        self.screenmanager = kwargs.pop('screenmanager', None)

        super(MenuPlaylist,self).__init__(**kwargs)


        self.cols = 2
        self.rows = 2
        # self.padding = 0

        columnWidth0 = Window.width * 0.3
        columnWidth1 = Window.width-columnWidth0
        headerHeight = 20
        headerText0 = "[b]Playlists[/b]"
        headerText1 = "[b]Media Files[/b]"

        headerColor0 = hexColor('#5a5560')#
        headerColor1 = hexColor('#2d4159')#(0.5,0.5,0,1)

        enaColor0 = [0.5,0.5,1,1]
        enaColor1 = [1,0.5,0.2,1]

        self.header0 = self.header = SelectLabelBg(
            background_color = headerColor0,
            text_size=(columnWidth0-20,headerHeight),
            text=headerText0,
            halign="center",
            valign="middle",
            size_hint_y=None,
            size_hint_x=None,
            height=headerHeight,
            width=columnWidth0,
            id="-1",
            markup = True
        )
        self.add_widget(self.header0)

        self.header1 = self.header = SelectLabelBg(
            background_color = headerColor1,
            text_size=(columnWidth0-20,headerHeight),
            text=headerText1,
            halign="center",
            valign="middle",
            size_hint_y=None,
            size_hint_x=None,
            height=headerHeight,
            width=columnWidth1,
            id="-1",
            markup = True
        )

        self.add_widget(self.header1)



        self.fileList = FileList(
            id=str(int(self.id)+1),
            rootdir=includes.config[os.name]['playlist']['rootdir'],
            enaColor=enaColor0,
            bar_width=10,
            size_hint_x=None,
            width=columnWidth0,
            supportedTypes=includes.config[os.name]['playlist']['types'],
            screenmanager=self.screenmanager,
            fillerColor=headerColor0,
            showDirs=False,
            selectFirst=False
        )

        self.files = PlaylistJsonList(
            id=str(int(self.id) + 5000),
            enaColor=enaColor1,
            bar_width=10,
            size_hint_x=None,
            width=columnWidth1,
            fillerColor=headerColor1,
        )


        self.add_widget(self.fileList)
        self.add_widget(self.files)

        self.mode = self._FILE_LIST

        #Fill the select List View with elements from the first json file
        # logging.debug("MenuVideo: before widget list iteration... len = {}".format(self.fileList.widgets))
        # for item in self.fileList.widgets:
        #     logging.debug("MenuVideo: found item in widgets item = {}".format(item))
        #     if "..." in item.text:
        #         continue
        #     elif item.text.endswith('.json'): #TODO this is not nicely implemented,
        #         self.updateJsonFiles(item.text)

        self.workThread = threading.Thread(target = self._processPlaylist)
        self.workThread.setDaemon(True)
        self.workThread.start()
        self.ctrlQueue = queue.Queue()


        self.prevTimestamp = time.time()
