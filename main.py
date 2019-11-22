import Xlib
import Xlib.display
import logging
import json
import time

import includes

from  subprocess import Popen, threading
from multiprocessing.connection import Listener

class IshaWm():
    displayWidth = None
    displayHeight = None
    display = None
    root = None
    activeWindow = None
    osdWin = None


    def __init__(self):
            self.display = Xlib.display.Display()
            self.root = self.display.screen().root
            self.displayWidth = self.root.get_geometry().width
            self.displayHeight = self.root.get_geometry().height
            self.root.change_attributes(event_mask = Xlib.X.SubstructureRedirectMask)
            self.handleActive = False
            self.mainGuiMapped = False
            self.state = 0

    first = True
    mainWin = None
    def handleEvents(self):
        if self.display.pending_events() > 0:
            event = self.display.next_event()
        else:
            return

        if event.type == Xlib.X.MapRequest:
            xClass = event.window.get_wm_class()

            #The first map request that comes from python is considered kivy root window
            #We start this window maximized always
            if self.state == 0 and 'python' in xClass[0]:
                event.window.configure(
                    width=self.displayWidth,
                    height=self.displayHeight,
                    x=0,
                    y=0
                )
                event.window.map()
                self.mainGuiMapped = True
                self.state = 1

            elif self.state == 1:
                #the second pyton app that is started is considered to be the OSD
                # and osd should be drawn on bottom of page with 50px fixed height
                if 'python' in xClass[0]:
                    osdHeight = 55
                    event.window.configure(
                        width=self.displayWidth,
                        height=osdHeight,
                        x=0,
                        y=self.displayHeight-osdHeight
                    )
                    event.window.map()
                    self.osdWin = event.window
                    self.osdBackground()

                else:
                    #any other window will be just mapped as is like mpv player
                    event.window.map()



    def osdTop(self):
        if self.osdWin is not None:
            #logging.error("Bring OSD to the top 1")
            self.osdWin.configure(stack_mode=Xlib.X.Above)
            #self.osdWin.configure(stack_mode=Xlib.X.TopIf)


    def osdBackground(self):
        if self.osdWin is not None:
            #logging.error("Bring OSD to the bottom")
            self.osdWin.configure(stack_mode=Xlib.X.BottomIf)


    def server(self):
        address = ('localhost', includes.config['ipcWmPort'])     # family is deduced to be 'AF_INET'
        listener = Listener(address, authkey=b'secret password')

        while True:
            #logging.error('before')
            conn = listener.accept()
            #logging.error('connection accepted from {}'.format(listener.last_accepted))

            while True:
                #logging.error('data =')
                try:
                    msg = conn.recv()
                    data = json.loads(msg)
                    #logging.error('data = {}'.format(data))

                    if 'cmd' in data:
                        cmd = data['cmd']

                        if cmd == 'osdTop':
                            self.osdTop()
                            #logging.error("Bring OSD to the top")

                        elif cmd == 'osdBackground':
                            self.osdBackground()
                            #logging.error("Bring OSD to the bot")

                except EOFError as e:
                    break

        listener.close()

    def main(self):

        self.thread = threading.Thread(target=self.server)
        self.thread.setDaemon(True)
        self.thread.start()

        self.handleActive = True

        while True:
            self.handleEvents()
            time.sleep(0.25)


def guiWorker():
    from main import Main
    Main().run()


if __name__ == "__main__":
    wm = IshaWm()
    wmThread = threading.Thread(target=wm.main)
    wmThread.setDaemon(True)
    wmThread.start()

    while not wm.handleActive:
        time.sleep(0.1)


    guiPro = Popen(["python3", "main.py"])

    while not wm.mainGuiMapped:
        time.sleep(0.1) #Wait so that everything opens in order

    osdPro = Popen(["python3", "menu_osd.py"])
    while wm.osdWin == None:
        time.sleep(0.1)


    time.sleep(5)
    while guiPro.poll() == None and osdPro.poll() == None:
        time.sleep(1)

    if osdPro.poll() == None:
        osdPro.kill()

    if guiPro.poll() == None:
        guiPro.kill()
