#from player import *
import logging
import subprocess
import os
import socket
import json
from functools import partial

from  subprocess import Popen, threading
from kivy.core.window import Window
import time
import includes
from  pymediainfo import MediaInfo



"""
This is the media player we use for isha pi project.
On Raspberri PI we will be using the openmx player.
On virtual machines and testing on windows we can use mpv player
"""
class Player():
    exec = None
    process = None
    screensaver = None
    screenManager = None
    isPlaying = False
    isPaused = False
    path = None
    runtime = 0
    vlcPl = None
    semaExec = threading.Semaphore()

    #
    # Playback functions the user need to set up if needed
    #
    def onPlayEnd(self):
        '''Callbakc function called when playback finished'''
        return

    #
    # Public functions of the player, each player class should have them
    #
    def stop(self):
        self._execute({'command': ["quit"]})

    def _getRunTime(self):
        ret = self._execute({'command': ["get_property", "time-pos"]})
        if ret is None:
            return

        tmp = json.loads(ret[0])
        if 'data' in tmp:

            self.runtime = int(tmp['data'])
            #logging.error("runtime value set.... = {}".format(self.runtime))

    def pause(self):
        # from random import randint as random
        # cmd = 'echo \'{ "command": ["cycle", "pause"], "request_id": %s }\'' % str(random(0,100))
        # cmd = cmd + "| socat - " + includes.config['tmpdir'] + "/socket"
        # logging.error(cmd)
        # os.system(cmd)
        self._execute({'command': ["set_property", "pause", True]})



    def play(self):
        # from random import randint as random
        # cmd = 'echo \'{ "command": ["set_property", "pause", false], "request_id": %s }\'' % str(random(100,200))
        # cmd = cmd + "| socat - " + includes.config['tmpdir'] + "/socket"
        # os.system(cmd)
        self._execute({'command': ["set_property", "pause", False]})

    def isPaused(self):
        ret = self._execute({'command': ["get_property", "pause"]})
        if ret is None:
            return

        #logging.error("Ret= {}".format(ret))
        tmp = json.loads(ret[0])

        if 'data' in tmp:
            return tmp['data']
        else:
            return None

    def togglePause(self):

        #self.isPaused = True
        val = self.isPaused()
        if value is not None:
            self._execute({'command': ["set_property", "pause", not val]})

    #
    # Private methods
    #
    socket = None
    sockPath = None
    def _conectToSocket(self, path):

        while not os.path.exists(path):
            time.sleep(0.5)

        self.sockPath = path
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.socket.connect(path)
        except OSError as e:
            self.socket = None
            #raise SocketError from e
            logging.error("SockerError")


    def _execute(self, command):
        self.semaExec.acquire()
        data = json.dumps(command) + "\r\n"
        data = bytes(data, encoding='utf-8')

        try:
            if self.socket:
                self.socket.send(data)
                buf = self.socket.recv(1024)
                if "error" not in str(buf):#we got event see read again... retry
                     buf = self.socket.recv(1024)
            else:
                logging.error("No socket in commmand")
                self.semaExec.release()
                return None
        except:
            logging.error("Problems in socket....")
            self.semaExec.release()
            return None

        #logging.error('DEBUG:data:: {}'.format(data))
        #logging.error('DEBUG:buffer:: {}'.format(buf))


        tmp = buf.decode('utf-8').split('\n')

        for item in tmp:
            result = json.loads(item)
            if not 'error' in result:
                self.semaExec.release()
                return None

            status = result['error']
            if status == 'success':
                self.semaExec.release()
                return tmp

        logging.error("Player: error value returned from player...")
        self.semaExec.release()

    def _command(self, command, *args):
        return self._execute({'command': [command, *args]})

    def close(self):
        self.socket.close()

    def _onUpdateRunTime(self, val):
        pass

    def _playWorkThread(self, mode):
        logging.debug("Thread mode = {}.....".format(mode))
        time.sleep(2)
        self._conectToSocket(os.path.join(includes.config['tmpdir'],"socket"))

        self.isPlaying = True
        if self.process == None:
            self.isPlaying = False
            self.onPlayEnd()
            return


        while self.process.poll() == None:
            time.sleep(1)

            #self.runtime = self.runtime + 1
            self._getRunTime()
            self._onUpdateRunTime(time.strftime('%H:%M:%S', time.gmtime(self.runtime)))

            if self.runtime % includes.config['settings']['runtimeInterval'] == 0:
                includes.db['runtime'] = self.runtime
                includes.db['mediaPath'] = self.path
                includes.writeDb()

        #-------------- End of playback ------------
        self.isPlaying = False
        includes.db['runtime'] = 0
        includes.db['mediaPath'] = ""
        includes.writeDb()

        self.onPlayEnd(None)




    def start(self, path, tSeek):
        logging.info("Player: start playing file... path = {}".format(path))
        self.path = path


        if not os.path.isfile(path):
            logging.error("Player: file not found [{}]".format(path))
            return

        videoFormats =  tuple(includes.config['video']['types'].split(','))
        audioFormats = tuple(includes.config['audio']['types'].split(','))

        logging.debug("Player: videoFormats = {} / audioFormats = {}".format(videoFormats, audioFormats))
        mode = "nothing"
        if path.lower().endswith(videoFormats):
            mode = "video"
            mediaInfo = MediaInfo.parse(path)

            videoWidth, videoHeight = 0, 0
            for track in mediaInfo.tracks:
                if track.track_type == 'Video':
                    videoWidth, videoHeight = track.width, track.height

            osdHeight = 50
            playerHeight = Window.height - (2*osdHeight)#videoHeight - osdHeight
            playerWidth = int(playerHeight * (videoWidth / videoHeight))


            posx = int((Window.width - playerWidth) / 2)
            posy = int((Window.height - playerHeight) / 2)

            logging.error("Player: playerWidth: {} / playerHeight: {} / videoWidth: {} / videoHeight: {} / posx: {} / posy: {}".format(
                playerWidth, playerHeight, videoWidth, videoHeight, posx, posy))


            self.isPlaying = True
            self.runtime = tSeek

            self.process = Popen(["mpv",
                            "--geometry={}+{}+{}".format(playerWidth, posx, posy),
                            #"--geometry=1244+98+0",
                            "--start=+{}".format(tSeek),
                            "--no-border",
                            "--no-input-default-bindings",
                            path,
                            "--really-quiet",
                            #"--no-osc",
                            #"--pause", #TODO: remove !!! ::TK::
                            "--no-input-terminal",
                            "--input-ipc-server={}".format(os.path.join(includes.config['tmpdir'],"socket"))

                            ])



        elif path.lower().endswith(audioFormats):
            self.isPlaying = True
            mode = "audio"
            logging.debug("Player: start playing audio")

            self.isPlaying = True
            self.process = Popen(["mpv",
                            "--start=+{}".format(tSeek),
                            "--no-border",
                            "--no-input-default-bindings",
                            path,
                            "--really-quiet",
                            "--no-osc",
                            "--no-input-terminal",
                            "--input-ipc-server={}".format(os.path.join(includes.config['tmpdir'],"socket"))
                            ])
        else:
            logging.debug("Player: no video nor audio file... {}".format(path))

        # Start player thread

        self.playThread = threading.Thread(target = self._playWorkThread, args=(mode,))
        self.playThread.setDaemon(True)
        self.playThread.start()

    def killPlayer(self):

        if self.process:
            self.process.kill()

        #wait for process to finish
        while self.process.poll() == None:
            time.sleep(0.25)

        #reset the runtime value
        self.runtime = 0
        self._onUpdateRunTime(time.strftime('%H:%M:%S', time.gmtime(self.runtime)))



if __name__ == "__main__":
    player = MpvPlayer()
    player._conectToSocket("/tmp/socket")
    player.getRunningTime()
