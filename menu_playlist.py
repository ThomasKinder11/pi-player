from  subprocess import threading
import queue
import time
import os
import logging
import json

from kivy.utils import get_color_from_hex as hexColor
from kivy.core.window import Window
import includes
from selectable_items import StackLayout, Select, SelectLabelBg, PlaylistJsonList
from menu_video import FileList

def createPlayListEntry(path, name, nodeId, start):
    tmp = {
        int(nodeId):{
            'path': path,
            'name': name,
            'pre' : "",
            'post' : "",
            'start' : start,
            'end' : 0
        }
    }
    return tmp


class MenuPlaylist(StackLayout, Select):
    _fileList = 0
    _jsonList = 1
    mode = _fileList
    select = "json"
    pList = None
    workThread = None
    ctrlQueue = None
    pListStartId = 0
    prevTimestamp = None

    def size_change(self, widget, value):
        columnWidth0 = Window.width * 0.3
        columnWidth1 = Window.width - columnWidth0
        headerHeight = includes.styles['playlistHeadHeight']

        self.header0.size = (columnWidth0, headerHeight)
        self.header1.size = (columnWidth1, headerHeight)

        self.fileList.size = (columnWidth0, value[1])
        self.files.size = (columnWidth1, value[1])


    def pos_change(self, widget, value):
        pass

    def osdEnable(self, args):
        #callback function to enable osd
        pass

    def osdDisable(self, args):
        pass #callback function to disable osd

    def osdColorIndicator(self, args):
        pass

    def hasNext(self, args):
        pass

    def hasPrevious(self, args):
        pass

    def hasNextTrack(self):
        return self.hasNext

    def hasPreviousTrack(self):
        return self.hasPrevious

    def isPaused(self):
        return not includes.player.isPlaying

    def isPlaying(self):
        return includes.player.isPlaying

    def pause(self, args):
        includes.player.pause()

    def play(self, args):
        includes.player.play()

    def seek(self, time):
        includes.player.seek(time)

    def enable(self, args):#down
        if self.fileList.widgets is None or len(self.fileList.widgets) <= 0:
            return True

        if self.mode == self._fileList  and len(self.fileList.widgets) > 0:
            tmpId = self.fileList.wId + 1

            if tmpId == len(self.fileList.widgets):
                tmpId = tmpId - 1

            self.updateJsonFiles(self.fileList.widgets[tmpId].text)
            ret = self.fileList.enable(None)

            return ret

        elif self.mode == self._jsonList:


            self.files.enable(None)
            return False

        return False

    def disable(self, args):#up
        if self.fileList.widgets is None or len(self.fileList.widgets) <= 0:
            return True

        if self.mode == self._fileList and len(self.fileList.widgets) > 0:
            tmpId = self.fileList.wId - 1
            if tmpId < 0:
                tmpId = 0


            self.updateJsonFiles(self.fileList.widgets[tmpId].text)

            return self.fileList.disable(None)

        elif self.mode == self._jsonList:
            self.files.disable({'disTop':False})
            return False

        return False

    def disableAll(self, args):
        for wid in self.fileList.widgets:
            wid.disable(None)


    def left(self, args):
        if self.mode == self._fileList:

            return True

        elif self.mode == self._jsonList:
            self.mode = self._fileList

            for wid in self.files.widgets:
                wid.disable({'inc':False})

            self.files.wId = -1

            #TODO: instead of text color, switch the background color if possible
            #tmpID = self.fileList.wId
            #self.fileList.widgets[tmpID].label.color = self.fileList.enaColor

        return False

    def right(self, args):
        if args is not None:
            enableFilesView = args.pop('enableFilesView', True)
        else:
            enableFilesView = True

        if self.mode == self._fileList and len(self.fileList.widgets) > 0:
            self.mode = self._jsonList

            self.files.wId = -1
            if enableFilesView:
                self.files.enable(None)

        elif self.mode == self._jsonList:
            pass

    def _validateJson(self, path):
        for i in range(len(self.pList)):
            if not str(i) in self.pList:
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
        path = os.path.join(includes.config['playlist']['rootdir'], text)

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
            self.files.add(self.pList[item]['name'], False)


    def _waitForCmd(self, key, value):
        while True:
            while self.ctrlQueue.empty():
                time.sleep(0.25)
                continue

            cmd = self.ctrlQueue.get()
            logging.debug("_waitForCmd: got cmd = {}...".format(cmd))
            cmd = cmd['cmd']

            if 'abort' in cmd:
                return 'abort'

            if 'previous' in cmd:
                return 'previous'

            if 'next' in cmd:
                return 'next'

            if value is not None:
                if key in cmd:
                    if cmd[key] == value:
                        return ('match', True)
            else:
                return ('cmd', cmd)



    def _previousNextContrl(self, mode, cmd, index, plistStart, isPre):
        doubleClickPrev = False
        skipFirst = False

        if 'previous' in cmd:
            if time.time() - self.prevTimestamp <= 3: #we have 3 seconds to skip to previous
                self.prevTimestamp = time.time()
                doubleClickPrev = True

            self.prevTimestamp = time.time()

            if isPre or doubleClickPrev:
                doubleClickPrev = False

                if index >= 1:
                    index = index - 1
                    self.files.disable(None)
                else:
                    index = 0
                    plistStart = 0

                plistStart = index

            if mode == "json":
                skipFirst = True

            return (True, index, plistStart, skipFirst)

        # elif 'next' in cmd:
        #       pass
        #

        #If nothing happens return original values
        return (False, index, plistStart, False)


    def _playListControl(self, playlist, plistStart, skipFirst, mode):
        i = 0
        skipPre = False

        while i < len(playlist):
            item = list(playlist.keys())[i]

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

            if 'pre' in playlist[item] and not skipPre:
                if playlist[item]['pre'] == 'BLACKSCREEN':
                    self.osdColorIndicator(includes.styles['plistIndicatorColor'])

                    ret = self._waitForCmd('key', 'enter')

                    self.osdColorIndicator(includes.colors['black'])
                    if 'abort' in ret:
                        return

                    ret = self._previousNextContrl(mode, ret, i, plistStart, True)
                    stat, i, plistStart, skipFirst = ret
                    if stat:
                        skipPre = True
                        continue

            skipPre = False

            # Play the mdia file with the player
            if 'start' in playlist[item]:
                tSeek = playlist[item]['start']
            else:
                tSeek = 0

            includes.player.start(playlist[item]['path'], tSeek)

            ret = self._waitForCmd('event', 'end')
            if 'abort' in ret:
                includes.player.killPlayer()
                return
            else:
                ret = self._previousNextContrl(mode, ret, i, plistStart, False)
                stat, i, plistStart, skipFirst = ret

                if includes.player.process:
                    includes.player.process.kill()

                if stat:
                    skipPre = True
                    continue

            if 'post' in playlist[item]:
                if 'PLAYNEXT' in playlist[item]['post']:
                    i = i + 1
                    continue

            i = i + 1

    def _processPlaylist(self):
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

        skipFirst = False
        while True:
            time.sleep(0.25)
            cmd = self._waitForCmd(None, None)
            if cmd[0] == 'cmd':
                cmd = cmd[1]
            else:
                logging.error("MenuPlayList._processPlaylist: command error [1]...")
                return

            #only when mode is defined its something we can process otherwise wait for next command
            if not 'mode' in cmd:
                continue

            self.osdEnable(None)

            if cmd['mode'] == "json": #started via file list viewer for PlayList
                if self.mode == self._fileList:
                    if len(self.fileList.children) > 0:
                        self.pListStartId = 0
                        text = self.fileList.widgets[self.fileList.wId].text
                        self.updateJsonFiles(text)
                        self.right({'enableFilesView':False})
                        skipFirst = False
                elif self.mode == self._jsonList:
                    skipFirst = True
                    self.pListStartId = self.files.wId
                else:
                    continue

                playlist = self.pList
                plistStart = self.pListStartId
            elif cmd['mode'] == "virtual":
                if 'playlist' in cmd:
                    playlist = cmd['playlist']
                    plistStart = 0


            includes.screenSaver.disable()
            self.screenmanager.current="blackscreen"

            self._playListControl(playlist, plistStart, skipFirst, cmd['mode'])

            self.osdDisable(None)
            includes.screenSaver.start(None)



    def abort(self, args):
        includes.player.stop()
        self.ctrlQueue.put({'cmd':{'abort':None}})

    def next(self, args):
        self.ctrlQueue.put({'cmd':{'next':None}})

    def previous(self, args):
        self.ctrlQueue.put({'cmd':{'previous':None}})

    def onPlayerEnd(self, args):
        self.ctrlQueue.put({'cmd':{'event':'end'}})


    def startVirtual(self, args):
        logging.debug("MenuPlayer: called startVirtual with args = {}".format(args))
        autoplay = args.pop('autoplay', False)

        if autoplay:
            logging.debug("MenuPlayer: autoplay branch...")
            path = args.pop('path', None)
            supportedTypes = args.pop('supportedTypes', None)
            dirname = os.path.dirname(path)
            files = os.listdir(dirname)
            files.sort()
            logging.debug("MenuPlayer: autoplay branch: files in directory = {}...".format(files))

            startFile = False
            virtPlaylist = {}
            i = 0

            for f in files:
                fDir = os.path.join(dirname, f)
                if os.path.isdir(fDir) or not f.lower().endswith(supportedTypes):
                    continue

                if fDir == path:
                    startFile = True

                if startFile:
                    tmp = createPlayListEntry(fDir, "VPL", i, 0)
                    virtPlaylist.update(tmp)
                    i = i + 1

                cmd = {
                    'cmd':{
                        'playlist': virtPlaylist,
                        'mode': 'virtual'
                    }
                }

            self.ctrlQueue.put(cmd)

        else:
            self.startVirtualSingle(args)

    def startVirtualSingle(self, args):
        path = args.pop('path', None)
        start = args.pop('start', 0)

        if path is None:
            logging.error("startVirtualSingle: path was not specified in arguments!...")
            return

        tmp = createPlayListEntry(path, "VPL", 0, start)

        cmd = {
            'cmd':{
                'playlist': tmp,
                'mode': 'virtual'
            }
        }

        self.ctrlQueue.put(cmd)

    def enter(self, args):
        if args is not None:
            mode = args.pop('mode', "json")
        else:
            mode = "json"

        self.ctrlQueue.put({
            'cmd':{'mode':mode, 'key':'enter'}})


    def __init__(self, **kwargs):
        self.selId = kwargs.pop('id', None)
        self.screenmanager = kwargs.pop('screenmanager', None)

        super(MenuPlaylist, self).__init__(**kwargs)

        self.cols = 2
        self.rows = 2

        columnWidth0 = Window.width * 0.3
        columnWidth1 = Window.width-columnWidth0
        headerHeight = includes.styles['playlistHeadHeight']
        headerText0 = "[b]Playlists[/b]"
        headerText1 = "[b]Media Files[/b]"



        self.header0 = SelectLabelBg(
            background_color=includes.styles['headerColor0'],
            text_size=(columnWidth0-20, headerHeight),
            text=headerText0,
            halign="center",
            valign="middle",
            size_hint_y=None,
            size_hint_x=None,
            height=headerHeight,
            width=columnWidth0,
            id="-1",
            markup=True
        )
        self.add_widget(self.header0)

        self.header1 = SelectLabelBg(
            background_color=includes.styles['headerColor1'],
            text_size=(columnWidth0-20, headerHeight),
            text=headerText1,
            halign="center",
            valign="middle",
            size_hint_y=None,
            size_hint_x=None,
            height=headerHeight,
            width=columnWidth1,
            id="-1",
            markup=True
        )

        self.add_widget(self.header1)

        self.fileList = FileList(
            id=str(int(self.selId)+1),
            rootdir=includes.config['playlist']['rootdir'],
            enaColor=includes.styles['enaColor0'],
            bar_width=10,
            size_hint_x=None,
            width=columnWidth0,
            supportedTypes=includes.config['playlist']['types'],
            screenmanager=self.screenmanager,
            fillerColor=includes.styles['headerColor0'],
            showDirs=False,
            selectFirst=False,
            showIcon=False,
        )

        self.files = PlaylistJsonList(
            id=str(int(self.selId) + 5000),
            enaColor=includes.styles['enaColor1'],
            bar_width=10,
            size_hint_x=None,
            width=columnWidth1,
            fillerColor=includes.styles['headerColor1'],
            showIcon=False,
        )


        self.add_widget(self.fileList)
        self.add_widget(self.files)

        self.mode = self._fileList
        self.workThread = threading.Thread(target=self._processPlaylist)
        self.workThread.setDaemon(True)
        self.workThread.start()
        self.ctrlQueue = queue.Queue()


        self.prevTimestamp = time.time()


        self.bind(size=self.size_change)
        self.bind(size=self.pos_change)
