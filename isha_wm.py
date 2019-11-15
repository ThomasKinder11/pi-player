import Xlib
import Xlib.display
import logging
import json
import time

from  subprocess import Popen, threading
from multiprocessing.connection import Listener

class IshaWm():
    displayWidth = None
    displayHeight = None
    display = None
    root = None
    activeWindow = None
    osdWin = None
    curState = 0

    def __init__(self):
            print("init called")
            self.display = Xlib.display.Display()
            self.root = self.display.screen().root
            self.displayWidth = self.root.get_geometry().width
            self.displayHeight = self.root.get_geometry().height
            self.root.change_attributes(event_mask = Xlib.X.SubstructureRedirectMask)
            #print("width = {} height = {}".format(self.displayWidth, self.displayHeight))

    first = True
    mainWin = None
    def handleEvents(self):
        if self.display.pending_events() > 0:
            event = self.display.next_event()
            print("Event type = {}".format(event.type))
        else:
            return

        if event.type == Xlib.X.MapRequest:
            print("IshaWM: map request received")
            print("name = {}".format(event.window.get_wm_name()))#Kivy does not set name somehow
            print("icnname = {}".format(event.window.get_wm_icon_name()))
            print("class = {}".format(event.window.get_wm_class()))
            print("geometry = {}".format(event.window.get_geometry()))
            print("properties = {}".format(event.window.list_properties()))

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
                self.state = 1

            elif self.state == 1:
                #the second pyton app that is started is considered to be the OSD
                # and osd should be drawn on bottom of page with 50px fixed height
                if 'python' in xClass[0]:
                    osdHeight = 50
                    event.window.configure(
                        width=self.displayWidth,
                        height=osdHeight,
                        x=0,
                        y=400
                        #y=self.displayWidth-osdHeight-100
                    )
                    event.window.map()
                    self.osdWin = event.window
                    self.osdBackground()

                else:
                    #any other window will be just mapped as is like mpv player
                    event.window.map()
                    #bring osd menu on top if we press a key


    def osdTop(self):
        if self.osdWin is not None:
            logging.error("Bring OSD to the top 1")
            self.osdWin.configure(stack_mode=Xlib.X.Above)
            #self.osdWin.configure(stack_mode=Xlib.X.TopIf)
            #self.osdWin.configure(stack_mode=Xlib.X.BottomIf)

    def osdBackground(self):
        if self.osdWin is not None:
            logging.error("Bring OSD to the bottom")
            self.osdWin.configure(stack_mode=Xlib.X.BottomIf)
            #self.osdWin.configure(stack_mode=Xlib.X.TopIf)
            #self.osdWin.configure(stack_mode=Xlib.X.BottomIf)

    def server(self):
        address = ('localhost', 6002)     # family is deduced to be 'AF_INET'
        listener = Listener(address, authkey=b'secret password')

        while True:
            logging.error('before')
            conn = listener.accept()
            logging.error('connection accepted from {}'.format(listener.last_accepted))

            while True:
                try:
                    msg = conn.recv()
                    data = json.loads(msg)

                    if 'cmd' in data:
                        cmd = data['cmd']

                        if cmd == 'osdTop':
                            self.osdTop()
                            logging.error("Bring OSD to the top")

                        elif cmd == 'osdBackground':
                            self.osdBackground()
                            logging.error("Bring OSD to the bot")

                except EOFError as e:
                    break

        listener.close()

    def main(self):
        self.state = 0

        self.thread = threading.Thread(target=self.server)
        self.thread.setDaemon(True)
        self.thread.start()

        while True:
            self.handleEvents()
            time.sleep(0.25)


def guiWorker():
    from main import Main
    logging.error("start Main()....")
    Main().run()


if __name__ == "__main__":
    print("IshaWM: handleEvents: called")
    #IshaWm().main()



    #from menu_osd import OSDMain
    wm = IshaWm()
    wmThread = threading.Thread(target=wm.main)
    wmThread.setDaemon(True)
    wmThread.start()
    time.sleep(5)

    guiPro = Popen(["python3", "main.py"])

    osdPro = Popen(["python3", "menu_osd.py"])
    #wm.osdBackground()


    # guiThread = threading.Thread(target=guiWorker)
    # guiThread.setDaemon(False)
    # guiThread.start()

    while guiPro.poll() == None:
        time.sleep(1)

    if osdPro.poll() == None:
        osdPro.kill()

    #th1 = threading.Thread(target=OSDMain().run)
    #th1.setDaemon(True)
    #+th1.start()
