import vlc
from time import sleep
import queue
from subprocess import threading
import sys
import time
import logging

import Xlib
import Xlib.display
from Xlib import  Xutil


class Player():
    vlcPlayer = None
    vlcInst = None
    evManager = None
    cmdQueue = None
    #event callback for other applications
    def onPlayEnd(self,args):
        global test
        test = False
        '''Callbac function called when playback finished'''
        return

    def _mediaPlayerEnd(self, event):
        self.cmdQueue.put({'cmd':'mediaPlayerEnd'})


    def _worker(self):
        '''Worker thread that receives evenet manager signals'''
        while True:
            sleep(0.5)
            tmp = self.cmdQueue.get()
            print(tmp)
            cmd = tmp['cmd']

            #event manager callbacs cannot call vlc functions so this is why this...
            if cmd == "mediaPlayerEnd":
                logging.error("Thomas: media player end called. ")
                #self.vlcPlayer.release()
                self.vlcPlayer.stop()
                self.window.unmap()

                self.onPlayEnd(None)


    #player control functions
    def stop(self):
        if self.vlcPlayer.is_playing:
            self.vlcPlayer.stop()

    def pause(self):
        if self.vlcPlayer.is_playing:
            self.vlcPlayer.pause()

    def play(self):
        self.vlcPlayer.play()

    def seek(self, tSeek):
        if self.vlcPlayer.is_seekable() and self.vlcPlayer.is_playing():
            self.vlcPlayer.set_time(tSeek*1000)

    def togglePause(self):
        self.vlcPlayer.pause()

    def start(self, path, tSeek):
        media = self.vlcInst.media_new(path)
        self.vlcPlayer.set_media(media)

        self._createXwindow()
        self.vlcPlayer.set_xwindow(self.window.id)

        self.vlcPlayer.play()
        #self.vlcPlayer.set_fullscreen(True)

        #seek must come after file is started
        self.vlcPlayer.set_time(tSeek*1000)
        #self.vlcPlayer.toggle_fullscreen()

    def killPlayer(self):
        if self.vlcPlayer.is_playing:
            self.vlcPlayer.stop()
            self.window.destroy()

    #player status
    def getRuntime(self):
        return self.vlcPlayer.get_time()
        pass

    def getCurrentTotalTime(self):
        pass

    def isPaused(self):
        if self.vlcPlayer.is_playing() == 1:
            return False
        elif self.vlcPlayer.is_playing() == 0:
            return True

        return None

    def isPlaying(self):
        return self.vlcPlayer.is_playing() == 1

    def _xEventHandler(self):
        while True:
            try:
                if self.display.pending_events() > 0:
                    e = self.display.next_event()
                    logging.error("Thomas: event = {}".format(e))
                #Handle event for destoy
            except Xlib.error.ConnectionClosedError:
                break #TODO: is this enough or does it need to be more sophisticated?

    def _createXwindow(self):
        self.display = Xlib.display.Display()
        self.screen = self.display.screen()
        self.window = self.screen.root.create_window(
            x=400,
            y=100,
            width=400,
            height=300,
            border_width=0,
            depth=self.screen.root_depth,
        )

        self.window.set_wm_normal_hints(
            flags = (Xutil.PPosition | Xutil.PSize | Xutil.PMinSize)
        )

        self.window.map()

        self.eventThread = threading.Thread(target = self._xEventHandler)
        self.eventThread.setDaemon(True)
        self.eventThread.start()



    def __init__(self):
        self.vlcInst = vlc.Instance()
        self.vlcPlayer = self.vlcInst.media_player_new()

        self.evManager = self.vlcPlayer.event_manager()
        self.evManager.event_attach(vlc.EventType.MediaPlayerEndReached, self._mediaPlayerEnd)

        self.cmdQueue = queue.Queue()
        self.workThread = threading.Thread(target = self._worker)
        self.workThread.setDaemon(True)
        self.workThread.start()




if __name__ == "__main__":
    # import Xlib
    # import Xlib.display
    # from Xlib import  Xutil
    logging.error("Thomas: in main")

    pl = Player()

    #
    # display = Xlib.display.Display()
    # screen = display.screen()
    # window = screen.root.create_window(
    #     x=600,
    #     y=100,
    #     width=400,
    #     height=300,
    #     border_width=0,
    #     depth=screen.root_depth,
    # )
    #
    # window.set_wm_normal_hints(
    #     flags = (Xutil.PPosition | Xutil.PSize | Xutil.PMinSize)
    # )
    #
    # window.map()
    #
    # print(window.id)
    #
    #
    #
    # def ev():
    #     started = False
    #
    #     while True:
    #         try:
    #             e = display.next_event()
    #
    #
    #
    #         except Xlib.error.ConnectionClosedError:
    #             sys.exit()
    #
    #
    # th = threading.Thread(target = ev)
    # th.setDaemon(True)
    # th.start()

    #time.sleep(3)
    #pl.vlcPlayer.set_xwindow(window.id)
    # pl.vlcPlayer.set_xwindow(0x5c00000)
    pl.start("/tmp/a.mp4", 0)



    while True:
        time.sleep(1)
        if pl.vlcPlayer.is_playing() != 1:
            break







    # pl = Player()
    #
    # for i in range(2):
    #     pl.start("/tmp/a.mp4", 0)
    #     pl.vlcPlayer.toggle_fullscreen()
    #     sleep(4)
    #     print(pl.isPaused())
    #     print(pl.vlcPlayer.get_xwindow())
    #     #pl.togglePause()
    #
    #     pl.vlcPlayer.toggle_fullscreen()
    #
    #     while test:
    #         sleep(2)
    #         print(pl.getRuntime())
    #         print(pl.isPaused())
    #
    #         #pl.stop()
    #
    #     sleep(4)
