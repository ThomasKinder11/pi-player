import threading
import logging

from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Rectangle, Color
from kivy.uix.button import Button
from kivy.app import App

from selectable_items import Select
from selectable_items import SelectButton
import includes


class MenuStrip(StackLayout):
    widgets = []

    def addItem(self, imgPath, id, content):
        selBtn = SelectButton(
            imgPath=imgPath,
            size_hint_y=None,
            height=60,
            size_hint_x=None,
            width=160
        )

        #keep a list of all children for nvigation purposes
        d = {
            "btn":selBtn,
            "id":id,
            "content":content
        }

        self.widgets.append(d)

        #add item to the menu so it will be visible
        self.add_widget(selBtn)


    def __init__(self, **kwargs):
        super(MenuStrip, self).__init__(**kwargs)
        self.orientation='lr-tb'
        self.size_hint_x = None
        self.width = 160
        #self.spacing = [0, 8]

class ImcTabView(Select, GridLayout):
    def enable(self, id):
        for widget in self.strip.widgets:
            if int(id) == int(widget['id']):
                widget['btn'].enable(None)
                self.clear_widgets()
                self.add_widget(self.strip)
                if widget['content'] is None:
                    logging.error("MenuContainer: widget content with id = {} is None".format(id))

                self.add_widget(widget['content'])
                self.curWidget = widget
                return

    def disable(self, id):
        for widget in self.strip.widgets:
            if int(id) == int(widget['id']):
                widget['btn'].disable(None)
                return

    def setContent(self, id, content):
        logging.error("Thomas: setContent called")
        for i in range(len(self.strip.widgets)):
            widget = self.strip.widgets[i]

            if int(id) == int(widget['id']):
                logging.error("Set content for id = {} / content = {}".format(id, content))
                self.strip.widgets[i]['content'] = content

                return

    def getMenuBtn(self, id):
        for widget in self.strip.widgets:
            if int(id) == int(widget['id']):
                return widget['btn']

    def update(self, args):
        logging.error("Thomas: update menu container")
        self.clear_widgets()
        self.add_widget(self.strip)
        self.add_widget(self.curWidget['content'])
        logging.error("Thomas: update content = {}".format(self.curWidget['content']))


    def __init__(self, **kwargs):
        idList = kwargs.pop('idList', [0,1,2,3,4])
        self.root = kwargs.pop('root', None)
        logging.error("Thomas: container kwargs = {}".format(kwargs))

        super(ImcTabView, self).__init__(**kwargs)

        self.rows = 1
        self.cols = 2
        self.spacing = [10,0]


        self.strip = MenuStrip()
        self.strip.addItem("atlas://resources/img/pi-player/power", idList[0], None)
        self.strip.addItem("atlas://resources/img/pi-player/video", idList[1], None)
        self.strip.addItem("atlas://resources/img/pi-player/music", idList[2], None)
        self.strip.addItem("atlas://resources/img/pi-player/playlist", idList[3], None)
        self.strip.addItem("atlas://resources/img/pi-player/settings", idList[4], None)

        self.add_widget(self.strip)
        self.curWidget = self.strip.widgets[0]

        with self.canvas.before:
            Color(*includes.colors['defaultGray'])
            Rectangle(size=self.size, pos=self.pos)


        self.bind(size=self.changeSize)


    def changeSize(self, widget, size):
        width0 = self.strip.widgets[0]['btn'].width

        with self.canvas.before:
            Color(*includes.colors['black'])
            Rectangle(size=(size[0], 2000), pos=self.pos)

            #Color(*includes.colors['defaultGray'])
            Color(*includes.colors['btngray'])
            Rectangle(size=(width0-5, 2000), pos=self.pos)












#############################
#############################
#############################
class Test(App):
    def testFunc(self):
        import time
        time.sleep(2)

        for i in range(5):
            self.menu.enable(i)
            self.menu.disable(i-1)
            time.sleep(1)





    def build(self):
        #strip = MenuStrip()
        self.menu = ImcTabView()



        workThread = threading.Thread(target=self.testFunc)
        workThread.setDaemon(True)
        workThread.start()

        return self.menu

if __name__ == '__main__':
    Test().run()
