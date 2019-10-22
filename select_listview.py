from kivy.graphics import Rectangle, Color, Line
from kivy.app import App
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.image import Image

from isha_pi_kivy import Select, SelectButton, SelectLabel
import logging


class SelectLabelBg(SelectLabel):
    def size_change(self, a, b):
        labelWidth = Window.width
        self.back.size = (self.parent.width, self.height)
        self.back.pos = self.pos

    def __init__(self,**kwargs):
        self.background_color = kwargs.pop('background_color', (1,1,1,0.5))
        super(SelectLabelBg,self).__init__(**kwargs)

        self.size_hint_x = None
        self.size_hint_y = None

        with self.canvas.before:
            Color(*self.background_color)
            self.back = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self.size_change)
        self.bind(pos=self.size_change)

class ImageBg(Widget):
    source = None

    def size_change(self, a, b):
        self.back.size = self.size
        self.back.pos = self.pos
        self.img.size = self.size
        self.img.pos = self.pos

    def __init__(self, **kwargs):
        self.imgSrc = kwargs.pop('source', None)
        self.background_color = kwargs.pop('background_color', (1,0,0,1))
        super(ImageBg, self).__init__(**kwargs)

        with self.canvas.before:
            Color(*self.background_color)
            self.back = Rectangle(size=self.size, pos=self.pos)

        with self.canvas:

            Color(1)
            self.img = Rectangle(source=self.imgSrc, size=self.size, pos=self.pos)

        self.bind(size=self.size_change)
        self.bind(pos=self.size_change)



class SelectListViewItem(StackLayout, Select):
    def changeSize(self, widget, value):
        self.label.width = Window.width-self.imgWidth
        self.label.text_size = (self.label.width-20,self.imgHeigth)

    def enable(self):
        self.label.enable()

    def disable(self):
        self.label.disable()

    def __init__(self, **kwargs):
        self.source = kwargs.pop('source', None)
        if not self.source:
            logging.error("SelectListViewItem: image not defined...")
            return

        self.enaColor = kwargs.pop('enaColor', (0,1,0,1))
        self.padding_top = kwargs.pop('padding_top', 0)
        self.background_color = kwargs.pop('background_color', (1,0,0,1))
        self.text = kwargs.pop('text', "undefined text")
        self.id = kwargs.pop('id', "undefined id")
        self.imgWidth = kwargs.pop('imgWidth', 100)
        self.imgHeigth = kwargs.pop('imgHeigth', 100)

        #set the layout hight to fit the image height
        self.height = self.imgHeigth + 2*self.padding_top
        self.size_hint_y= None

        super(SelectListViewItem, self).__init__(**kwargs)

        self.filler = SelectLabel(
            size_hint_x = None,
            width=20,
            size_hint_y=None,
            height=self.imgHeigth,
            id="-1",
            text_size = (0,0)
        )
        self.add_widget(self.filler)

        self.image = ImageBg(background_color=self.background_color, width=self.imgWidth, size_hint= (None, None), height=self.imgHeigth, source=self.source)
        self.add_widget(self.image)


        labelWidth = Window.width-self.imgWidth-self.filler.width
        self.label = SelectLabelBg(
            background_color = self.background_color,
            text_size=(labelWidth-20,self.imgHeigth),
            enaColor=self.enaColor,
            text=self.text,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=self.imgHeigth,
            size_hint_x=None,
            width=labelWidth,
            id=self.id
        )

        self.add_widget(self.label)

class SelectListView(Select, ScrollView):
    tmp = []
    layout = None
    widgets = []
    startId = None
    wId = 0 # id of the currently selected entry
    dir = "down"


    def enter(self):
        logging.info("SelectListView: enter callback triggered")

    def enable(self):

        if self.wId < len(self.widgets) - 1:
            self.wId = self.wId + 1
            self.widgets[self.wId].enable()
            self.scroll_to(self.widgets[self.wId])

            if self.wId > 0:
                self.widgets[self.wId-1].disable()

        return False # never returns true as there nothing we need to do when we come to end of list


    def disable(self):

        if self.wId >= 1:
            self.widgets[self.wId].disable()

            self.wId = self.wId - 1
            self.widgets[self.wId].enable()
            self.scroll_to(self.widgets[self.wId])

        else:
            return True

        return False


    def add(self, text, isDir):
        id = str(len(self.widgets) + self.startId)

        source = source="./resources/img/empty.png"
        if isDir:
            source="./resources/img/dir.png"


        bg = None
        if len(self.widgets) % 2 == 0:
            bg = (0.2,0.2,0.2,1)
        else:
            bg = (0.1,0.1,0.1,1)

        self.widgets.append(SelectListViewItem(
            enaColor=self.enaColor,
            source=source,
            background_color=bg,
            text=text,
            id=id,
            imgWidth=46,
            imgHeigth=46
            )

        )

        self.layout.add_widget(self.widgets[-1])



    def __init__(self, **kwargs):
        self.enaColor = kwargs.pop('enaColor', None)
        logging.error("enaCOlor = {}".format(self.enaColor))
        if not self.enaColor:
            logging.error("start id not set")
            return

        self.startId = int(kwargs['id']) + 1
        if not self.startId:
            logging.error("start id not set")
            return

        super(SelectListView, self).__init__(**kwargs)

        self.isSelectable = True
        self.wId = -1
        self.layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.size_hint_y=None
        self.height= Window.height-100

        self.add_widget(self.layout)


if __name__ == "__main__":
    class Main(App):
        def build(self):
            return SelectListViewItem(source="./resources/img/arrow.png", text="gurcken brot", imgWidth=50, imgHeigth=50,background_color=(0.3,0.3,0.3,1))# bg = (0.6,0.6,0.6,1))
            
    Main().run()
