import logging
import threading
import time
import queue
import sys
import globals



class ScreenSaver():
    ctrlQueue = None
    thread = None
    idleCounter = 0
    timeStep = 0.25
    saverTimeout = 5
    active = None
    ena = False

    def _worker(self):
        logging.info("ScreenSaver: thread called...")

        while True:
            time.sleep(self.timeStep)
            self.idleCounter = self.idleCounter + self.timeStep

            #just limit the counter value
            if self.idleCounter > globals.config['settings']['screensaverTime'] and self.ena:
                self.idleCounter = globals.config['settings']['screensaverTime']
                self.screenManager.current = self.blackScreenName
                self.active = True

            if not self.ctrlQueue.empty():
                cmd = self.ctrlQueue.get()

                if cmd['cmd'] == 'reset':
                    self.idleCounter = 0
                    self.screenManager.current=self.menuName
                    self.active = False

                elif cmd['cmd'] == 'stop':
                    logging.info("ScreenSaver: thread stopped...")
                    break;

                elif cmd['cmd'] == 'disable':
                    self.ena  = False
                    self.screenManager.current=self.menuName
                    self.idleCounter = 0
                    self.active = False

                elif cmd['cmd'] == 'enable':
                    self.ena = True
                    self.idleCounter = 0
                    self.active = False
                    self.screenManager.current=self.menuName


    def resetTime(self):
        if self.ena:
            self.ctrlQueue.put({'cmd':'reset'})

    def disable(self):
        logging.error("ScreenSaver: ßßßßßßßßßßß: trying to disable...")

        if self.ena:
            logging.error("ScreenSaver: ßßßßßßßßßßß: disable ")
            self.ctrlQueue.put({'cmd':'disable'})
            while self.ena:
                time.sleep(0.5)
                logging.debug("ScreenSaver: disable wait ....")
                pass


    def enable(self):
        logging.error("ScreenSaver: ßßßßßßßßßßß: enabled ")
        self.ctrlQueue.put({'cmd':'enable'})


    def __init__(self, screenManager, blackScreenName, menuName):
        logging.info("ScreenSaver: init: called")
        #self.ctrlQueue= queue.Queue()
        self.ctrlQueue = queue.Queue()
        self.thread = threading.Thread(target=self._worker)
        self.thread.setDaemon(True)
        self.screenManager = screenManager
        self.idleCounter = 0
        self.blackScreenName = blackScreenName
        self.menuName = menuName
        self.active = False


        self.thread.start()
