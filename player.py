from player import *
import logging
import os
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
    supportedPlayers = {}
    process = None
    screensaver = None
    screenManager = None
    isPlaying = False
    isPaused = False
    path = None
    runtime = 0
    vlcPl = None

    def onPlayEnd(self):
        return

    def _onUpdateRunTime(self, val):
        pass

    def _playWorkThread(self, mode):
        logging.debug("Thread mode = {}.....".format(mode))

        # if mode == 'audio':
        #     while self.vlcPl.is_playing():
        #         time.sleep(1)
        #         logging.debug("Wait for VLC to stop.....")
        #
        # elif mode == 'video':
        self.isPlaying = True
        if self.process == None:
            self.isPlaying = False
            self.onPlayEnd()
            return


        while self.process.poll() == None:
            time.sleep(1)

            self.runtime = self.runtime + 1
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

    def stop(self):
        if os.name == "posix":
            if self.process.poll():
                cmd = 'echo \'{ "command": ["quit"] }\''
                cmd = cmd + "| sudo socat - " + includes.config[os.name]['tmpdir'] + "/socket"
                os.system(cmd)

    def pause(self):
        self.isPaused = True



        if os.name == "posix":
            cmd = 'echo \'{ "command": ["set_property", "pause", true] }\''
            cmd = cmd + "| sudo socat - " + includes.config[os.name]['tmpdir'] + "/socket"
            #os.system('echo \'{ "command": ["set_property", "pause", true] }\' | sudo socat - /home/thomas/tmp/socket')
            os.system(cmd)




    def play(self, path, tSeek):
        logging.info("Player: start playing file... path = {}".format(path))
        self.path = path


        if not os.path.isfile(path):
            logging.error("Player: file not found")
            return

        videoFormats =  tuple(includes.config[os.name]['video']['types'].split(','))
        audioFormats = tuple(includes.config[os.name]['audio']['types'].split(','))

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
            self.process = Popen([self.supportedPlayers[os.name],
                            "--geometry={}+{}+{}".format(playerWidth, posx, posy),
                            #"--geometry=1244+98+0",
                            "--start=+{}".format(tSeek),
                            "--no-border",
                            "--no-input-default-bindings",
                            path,
                            #"--really-quiet",
                            #"--no-osc",
                            "--ontop",
                            "--input-ipc-server={}".format(os.path.join(includes.config[os.name]['tmpdir'],"socket"))

                            ])

        elif path.lower().endswith(audioFormats):
            self.isPlaying = True
            mode = "audio"
            logging.debug("Player: start playing audio with vlc...")

            #self.vlcPl = vlc.MediaPlayer(path)
            #self.vlcPl.play()
            #self.process = Popen(['vlc', path, "-I dummy --dummy-quiet"])
        else:
            logging.debug("Player: no video nor audio file... {}".format(path))

        # Start player thread
        self.playThread = threading.Thread(target = self._playWorkThread, args=(mode,))
        self.playThread.setDaemon(True)
        self.playThread.start()
#"--really-quiet",
#"--no-osc",

# "--input-ipc-server={}".format(os.path.join(includes.config[os.name]['tmpdir'], "ishapiSocket")
    def killPlayer(self):

        if self.process:
            self.process.kill()

        #wait for process to finish
        while self.process.poll() == None:
            time.sleep(0.25)

        #reset the runtime value
        self.runtime = 0
        self._onUpdateRunTime(time.strftime('%H:%M:%S', time.gmtime(self.runtime)))





    def __init__(self):#, screenManager, screenSaver):
        self.supportedPlayers['nt'] = "mpv.exe"
        self.supportedPlayers['posix'] = "mpv"
