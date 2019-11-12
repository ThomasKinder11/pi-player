

class Player():
    _isPlaying = False

    def isPlaying(self):
        return self._isPlaying

    def play(self, args):
        path = args.pop('path', None)
        print("try to load player")
        self.command('loadfile', path)
        print("player started")
        self.isPlaying = True

    def togglePlayPause(self):
        tmp = self.get_property("pause")
        if tmp:
            self.set_property("pause", False)
        else:
            self.set_property("pause", True)

    def seek(self, position):
         self.command("seek", position, "absolute")



if __name__ == "__main__":
    ply = MpvPlayer()
    print("start player")
    ply.play({'path':'C:\\tmp\\ishaPi2\\videos\\a.mp4'})
