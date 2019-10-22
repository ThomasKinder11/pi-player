from isha_pi_kivy import *
import logging
import globals
from volume_widget import VolumeIndicator

from kivy.uix.stacklayout import StackLayout
from kivy.app import App
from kivy.core.window import Window

class MenuOSD(StackLayout):
    btnPrevious = None
    btnNext = None
    btnPlay = None
    btnPaus = None
    btnStop = None
    volume = None
    id = None
    gab = None

    def changeSize(self, widget, value):
        self.gap.width = Window.width-(6*50)-10

    def volumeUp(self):
        self.volume.volumeUp()

    def volumeDown(self):
        self.volume.volumeDown()

    def muteToggle(self):
        self.volume.muteToggle()

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id', None)

        if self.id == None:
            logging.error("MenuOSD: id not defined...")
            return

        self.id = int(self.id)

        super(MenuOSD, self).__init__()

        self.btnPrevious = SelectButton(
            imgPath= "./resources/img/previous",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(self.id + 3)
        )



        self.btnNext = SelectButton(
            imgPath= "./resources/img/next",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(self.id + 0)
        )

        self.btnPlay = SelectButton(
            imgPath= "./resources/img/play",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(self.id + 1)
        )

        self.btnPause = SelectButton(
            imgPath= "./resources/img/pause",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(self.id + 2)
        )

        self.btnStop = SelectButton(
            imgPath= "./resources/img/stop",
            size_hint_y=None,
            size_hint_x=None,
            height=50,
            width=50,
            id=str(self.id + 3)
        )

        self.volume = VolumeIndicator(
            incVal=1,
            size_hint=(None, None),
            width=50,
            height=50,
            radius=15,
            bgColor=(0.4,0.4,0.4,1),
            color=(0, 0, 1, 0.5),
            value=0
        )

        self.gap = Label(

            size_hint_y=None,
            size_hint_x=None,
            padding_x=200,
            height=50,
            width=Window.width-(6*50)-10,
            id=str(self.id + 3)
        )

        self.add_widget(self.btnPause)
        self.add_widget(self.btnPlay)
        self.add_widget(self.btnStop)
        self.add_widget(self.btnPrevious)
        self.add_widget(self.btnNext)
        self.add_widget(self.gap)
        self.add_widget(self.volume)


        self.height = 50
        self.size_hint_y = None

        self.bind(size=self.changeSize)







class OSDMain(App):
    def build(self):
        return MenuOSD(id="0")

if __name__ == "__main__":
    #Window.size = (Window.width, 50)
    OSDMain().run()
