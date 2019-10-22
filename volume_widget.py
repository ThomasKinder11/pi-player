from kivy.graphics import Rectangle, Color, Line
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.widget import Widget
from kivy.uix.stacklayout import StackLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.core.window import Window

import logging
import threading
import time
import queue
import sys

class VolumeIndicator(RelativeLayout):
    label = None
    labelColor = ObjectProperty((1,1,1,1))
    muteState = ObjectProperty(False)
    value = ObjectProperty(None, allownone=True)
    bgColor = None
    oldVolume = 0
    incVal = 5
    tmpCanvas = None
    visible = None
    timeoutVal = 5
    timeoutThread = None
    timeInterval = 0
    ctrlQueue = None

    def _threadWorker(self):
        length = int(self.timeoutVal / self.timeInterval)
        cnt = 0

        while True:
            if not self.ctrlQueue.empty():

                cmd = self.ctrlQueue.get(False)

                if cmd['cmd'] == "reset":
                    logging.debug("VolumeThread: execute reset cmd")
                    cnt = 0
                    #self.enable()
                elif cmd['cmd'] == "stop":
                    cnt = 0
                    self._disable()
                    logging.debug("VolumeThread: stop thread")
                    break

                self.ctrlQueue.task_done()


            #Disable object if time get greater then timeoutThread
            if cnt  >= self.timeoutVal :
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
                self.indicator.bgColor=(1,0,0,1)
                self.indicator.color=(1,0,0,1)
                self.label.color = (1,0,0,1)
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

        if self.value >= 100:
            self.value = 100
            return

        self.value  = (self.value + self.incVal)


    def volumeDown(self):
        self._enable()

        if self.muteState:
            self.muteState = False

        if self.value <= 0:
            self.value = 0
            return

        self.value  = (self.value - self.incVal)

    def mute(self, widget, value):
        if not self.muteState: #we are muted
            self.indicator.bgColor=self.bgColor
            self.indicator.color=self.color
            self.label.color = self.labelColor
            self.value = self.oldVolume
        else:
            self.indicator.bgColor=(1,0,0,1)
            self.indicator.color=(1,0,0,1)
            self.label.color = (1,0,0,1)
            self.oldVolume = self.value
            self.value = 0

    def changeLabelColor(self, widget, value):
        if not value:
            return

        self.label.color = value

    def updateVal(self, widget, value):
        if value <0 or value > 100:
            return -1

        self.label.text = str(value)
        self.indicator.value = value
        self.value = value

    def _drawCanvas(self):
        self.indicator = CirularIndicator(
            size_hint=(None, None),
            width=self.width,
            height=self.height,
            radius=self.radius,
            bgColor=self.bgColor,
            color=self.color,
            value=self.value
        )

        self.add_widget(self.indicator)

        self.label = Label(
            text=str(self.value),
            color=self.labelColor,
            size_hint=(None, None),
            width=self.width+5,
            height=self.height+5,
            valign="middle",
            halign="center"
        )

        self.add_widget(self.label)
        self.visible = True

    def release(self):
        self.ctrlQueue.put({'cmd':'stop'})
        time.sleep(1)

    def __init__(self, **kwargs):
        self.bgColor = kwargs.pop('bgColor', (1,1,1,1))
        self.color = kwargs.pop('color', (1,1,1,1))
        self.value = kwargs.pop('value', 0)
        self.radius = kwargs.pop('radius', None)
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        self.incVal = kwargs.pop('incVal', 5)
        self.timeInterval = 0.100

        super(VolumeIndicator, self).__init__(**kwargs)

        self.bind(value = self.updateVal)
        self.bind(muteState = self.mute)
        self.bind(labelColor = self.changeLabelColor)

        self.ctrlQueue = queue.Queue()
        self.timeoutThread = threading.Thread(target=self._threadWorker)
        self.timeoutThread.setDaemon(True)

        self.timeoutThread.start()
        self.muteState = False





class CirularIndicator(Widget):
    value = ObjectProperty(0)
    color = ObjectProperty(None, allownone=True)
    bgColor = ObjectProperty(None, allownone=True)
    radius = None

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

        if value <0 or value > 100:
            return -1

        max = (value / 100.0) * 360.0

        self.line.circle = (self.width/2+3,self.height/2+3,self.radius,0,int(max))
        self.canvas.ask_update()

    def _drawCanvas(self):
        with self.canvas:
            if not self.bgColor or not self.color:
                logging.error("CircularIndicator: bgColor or color not set [{} / {}]".format(self.bgColor, self.color))
                return

            self.bgc = Color(*self.bgColor)
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
            max = (self.value / 100.0) * 360.0
            self.line = Line(
                circle=(
                    self.width/2+3,
                    self.height/2+3,
                    self.radius,
                    0,
                    max
                ),
                width=3
            )


    def __init__(self, **kwargs):
        self.bgColor = kwargs.pop('bgColor', (1,1,1,1))
        self.color = kwargs.pop('color', (1,1,1,1))
        self.value = kwargs.pop('value', 0)
        self.radius = kwargs.pop('radius', 10)
        super(CirularIndicator, self).__init__(**kwargs)

        self._drawCanvas()

        self.bind(value = self.updateVal)
        self.bind(bgColor = self.changeBG)
        self.bind(color = self.changeColor)




#-------------------------------------------------------------------------------
#-- Standalone test
#-------------------------------------------------------------------------------
if __name__ == "__main__":


    class Test(App):
        testVal = 0
        volume = None

        def volume_up(self, widget):
            self.volume.volumeUp()

        def volume_down(self, widget):
            self.volume.volumeDown()

        def mute(self, widget):
            logging.error("Thomas: change bg pressed")
            self.volume.muteToggle()

        def stop_btn(self, widget):
            Window.close()
            App.get_running_app().stop()




        def build(self):
            #self.indicator = CirularIndicator(size_hint=(None, None), width=50, height=50, radius=15, bgColor=(0.4,0.4,0.4,1), color=(0, 0, 1, 0.5), value=0)
            self.volume = VolumeIndicator(incVal=1, size_hint=(None, None), width=50, height=50, radius=15, bgColor=(0.4,0.4,0.4,1), color=(0, 0, 1, 0.5), value=0)
            #self.indicator.bgColor=(0.4,0.4,0.4,1)

            layout = StackLayout()
            layout.add_widget(self.volume)

            up = Button(text="volume up", size_hint=(None, None), width=100, height=100, pos=(100,100))
            up.bind(on_press=self.volume_up)
            layout.add_widget(up)

            down = Button(text="volume down", size_hint=(None, None), width=100, height=100, pos=(100,100))
            down.bind(on_press=self.volume_down)
            layout.add_widget(down)

            m = Button(text="Mute", size_hint=(None, None), width=100, height=100, pos=(210,100))
            m.bind(on_press=self.mute)
            layout.add_widget(m)

            stop = Button(text="stop", size_hint=(None, None), width=100, height=100, pos=(210,100))
            stop.bind(on_press=self.stop_btn)
            layout.add_widget(stop)

            return layout

    Test().run()
