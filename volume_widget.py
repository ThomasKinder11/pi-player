import logging
import threading
import time
import queue
import os

from kivy.graphics import Color, Line, Rectangle
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.stacklayout import StackLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.core.window import Window

import includes

class VolumeIndicator(RelativeLayout):
    label = None
    labelColor = ObjectProperty(includes.styles['volumeIndicatorColor'])
    muteState = ObjectProperty(False)
    value = ObjectProperty(100, allownone=True)
    bgColor = None
    oldVolume = 0
    incVal = 5
    tmpCanvas = None
    visible = None
    timeoutVal = 5
    timeoutThread = None
    timeInterval = 0
    ctrlQueue = None
    indicator = None

    def _threadWorker(self):
        cnt = 0

        while True:
            if not self.ctrlQueue.empty():

                cmd = self.ctrlQueue.get(False)

                if cmd['cmd'] == "reset":
                    cnt = 0

                elif cmd['cmd'] == "stop":
                    cnt = 0
                    self._disable()
                    break

                self.ctrlQueue.task_done()


            #Disable object if time get greater then timeoutThread
            if cnt >= self.timeoutVal:
                self._disable()

            cnt = cnt + self.timeInterval
            time.sleep(self.timeInterval)

    def _disable(self):
        if not self.muteState:
            if self.visible:
                self.canvas.clear()
                self.visible = False

    def _enable(self):
        self.ctrlQueue.put({'cmd':"reset"})

        if not self.visible:
            self._drawCanvas()
            if self.muteState:
                self.indicator.bgColor = (1, 0, 0, 1)
                self.indicator.color = (1, 0, 0, 1)
                self.label.color = (1, 0, 0, 1)
                self.value = 0

    def muteToggle(self):
        if self.muteState:
            self.muteState = False
        else:
            self._enable()
            self.muteState = True



    def volumeUp(self):
        self._enable()

        if self.muteState:
            self.muteState = False

        self.value = includes.clipInt(self.value + self.incVal, 0, 100)



    def volumeDown(self):
        self._enable()

        if self.muteState:
            self.muteState = False

        self.value = includes.clipInt(self.value - self.incVal, 0, 100)


    def mute(self, widget, value):
        if not self.muteState: #we are muted
            self.indicator.bgColor = self.bgColor
            self.indicator.color = self.color
            if self.label:
                self.label.color = self.labelColor
            self.value = self.oldVolume

        else:
            self.indicator.bgColor = (1, 0, 0, 1)
            self.indicator.color = (1, 0, 0, 1)
            if self.label:
                self.label.color = (1, 0, 0, 1)
            self.oldVolume = self.value
            self.value = 0


    def changeLabelColor(self, widget, value):
        if not value:
            return

        self.label.color = value

    def updateVal(self, widget, value):
        if value < 0 or value > 100:
            return -1

        if self.label:
            self.label.text = str(value)

        if self.indicator is not None:
            self.indicator.value = value

        self.value = value
        

        return 0

    def _drawCanvas(self):

        self.indicator = Indicator(
            size_hint=(None, None),
            width=self.width,
            height=self.height,
            radius=self.radius,
            bgColor=self.bgColor,
            color=self.color,
            value=self.value,
            mode=self.mode
        )

        self.add_widget(self.indicator)
        self.visible = True

    def release(self):
        self.ctrlQueue.put({'cmd':'stop'})
        time.sleep(1)

    def __init__(self, **kwargs):
        self.bgColor = kwargs.pop('bgColor', (1, 1, 1, 1))
        self.color = kwargs.pop('color', (1, 1, 1, 1))
        self.value = kwargs.pop('value', 0)
        self.radius = kwargs.pop('radius', None)
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        self.incVal = kwargs.pop('incVal', 5)
        self.mode = kwargs.pop('mode', 'line')
        self.timeInterval = 0.100

        super(VolumeIndicator, self).__init__(**kwargs)

        self.bind(value=self.updateVal)
        self.bind(muteState=self.mute)
        self.bind(labelColor=self.changeLabelColor)

        self.ctrlQueue = queue.Queue()
        self.timeoutThread = threading.Thread(target=self._threadWorker)
        self.timeoutThread.setDaemon(True)

        self.timeoutThread.start()
        self.muteState = False

        self.value = 100




class LinearIndicator(Widget):
    value = ObjectProperty(0)
    color = ObjectProperty(None, allownone=True)
    bgColor = ObjectProperty(None, allownone=True)



class Indicator(Widget):
    value = ObjectProperty(0)
    color = ObjectProperty(None, allownone=True)
    bgColor = ObjectProperty(None, allownone=True)
    radius = None
    line = None

    def changeBG(self, widget, value):
        if not value:
            return

        self.bgc = value
        self.canvas.clear()
        self._drawCanvas()

    def changeColor(self, widget, value):
        if not value:
            return

        self.c = value
        self.canvas.clear()
        self._drawCanvas()

    def updateVal(self, widget, value):
        if value < 0 or value > 100:
            return -1

        if self.mode == "line":
            self.line.size = (int(self.width  * (value / 100)), 20)

        else:
            maxVal = int((value / 100.0) * 360.0)
            self.line.circle = (self.width/2+3, self.height/2+3, self.radius, 0, maxVal)

        self.canvas.ask_update()

        return 0

    def _drawCanvas(self):
        with self.canvas:
            if not self.bgColor or not self.color:
                return

            self.bgc = Color(*self.bgColor)

            if self.mode == 'circle':
                self.bgLine = Line(
                    circle=(
                        self.width/2+3,
                        self.height/2+3,
                        self.radius,
                        0,
                        360
                    ),
                    width=3
                )

                self.c = Color(*self.color)
                maxVal = int((self.value / 100.0) * 360.0)
                self.line = Line(
                    circle=(
                        self.width/2+3,
                        self.height/2+3,
                        self.radius,
                        0,
                        maxVal
                    ),
                    width=3
                )

            elif self.mode == 'line':
                posY = (self.height-20)/ 2
                self.bgLine = Rectangle(pos=(0, posY), size=(self.width, 20))


                self.c = Color(*self.color)
                width = int(self.width  * (self.value / 100))
                self.line = Rectangle(pos=(0, posY), size=(width, 20))


    def __init__(self, **kwargs):
        self.bgColor = kwargs.pop('bgColor', (1, 1, 1, 1))
        self.color = kwargs.pop('color', (1, 1, 1, 1))
        self.value = kwargs.pop('value', 0)
        self.radius = kwargs.pop('radius', 10)
        self.mode = kwargs.pop('mode', 'circle')
        super(Indicator, self).__init__(**kwargs)

        self._drawCanvas()

        self.bind(value=self.updateVal)
        self.bind(bgColor=self.changeBG)
        self.bind(color=self.changeColor)

        #set volume to 100% which each start of the application




#-------------------------------------------------------------------------------
#-- Standalone test
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    import logging

    class Test(App):
        testVal = 0
        volume = None

        def toogleMode(self, widget):
            logging.error("toogle called {}".format(self.volume.mode))
            if self.volume.mode == 'cirle':
                self.volume.mode = 'line'
            elif self.volume.mode == 'line':
                self.volume.mode = 'circle'

        def volumeUp(self, widget):
            self.volume.volumeUp()

        def volumeDown(self, widget):
            self.volume.volumeDown()

        def mute(self, widget):
            self.volume.muteToggle()

        def stopBtn(self, widget):
            Window.close()
            App.get_running_app().stop()

        def build(self):
            self.volume = VolumeIndicator(
                incVal=10,
                size_hint=(None, None),
                width=100,
                height=50,
                radius=15,
                bgColor=includes.styles['volumeIndicatorBG'],
                color=includes.styles['volumeIndicatorColor'],
                value=0,
                mode='line'
            )

            layout = StackLayout()
            layout.add_widget(self.volume)

            upBtn = Button(
                text="volume up",
                size_hint=(None, None),
                width=100,
                height=100,
                pos=(100, 100)
            )
            upBtn.bind(on_press=self.volumeUp)
            layout.add_widget(upBtn)

            downBtn = Button(
                text="volume down",
                size_hint=(None, None),
                width=100,
                height=100,
                pos=(100, 100)
            )

            downBtn.bind(on_press=self.volumeDown)
            layout.add_widget(downBtn)

            muteBtn = Button(
                text="Mute",
                size_hint=(None, None),
                width=100,
                height=100,
                pos=(210, 100)
            )
            muteBtn.bind(on_press=self.mute)
            layout.add_widget(muteBtn)

            stopBtn = Button(
                text="stop",
                size_hint=(None, None),
                width=100,
                height=100,
                pos=(210, 100)
            )

            stopBtn.bind(on_press=self.stopBtn)
            layout.add_widget(stopBtn)

            tglModeBtn = Button(
                text="Toggle Mode",
                size_hint=(None, None),
                width=100,
                height=100,
                pos=(210, 100)
            )

            tglModeBtn.bind(on_press=self.toogleMode)
            layout.add_widget(tglModeBtn)

            return layout

    Test().run()
