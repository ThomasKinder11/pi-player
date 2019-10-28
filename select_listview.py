from kivy.graphics import Rectangle, Color, Line
from kivy.app import App
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.properties import ObjectProperty

from isha_pi_kivy import Select, SelectButton, SelectLabel
import logging, os, sys
import globals
import json


class SelectLabelBg(SelectLabel):
    background_color = ObjectProperty((1,1,1,0.5))

    def size_change(self, a, b):
        #labelWidth = Window.width
        self.back.size = (self.width, self.height)
        self.back.pos = self.pos

    def updateBg(self, widget, value):
        self.canvas.ask_update()

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
        self.bind(background_color=self.updateBg)
        self.bind(enaColor=self.updateBg)

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
    background_color = ObjectProperty((1,1,1,0.5))
    fillerColor=ObjectProperty((0,0,0.5,0.3))
    image = None
    label = None
    filler = None
    isDir = False
    user = {}

    def resize(self, widget, value):
        self.label.width = self.parent.width-self.imgWidth-self.filler.width
        self.label.text_size = (self.label.width-20,self.imgHeight)
        pass

    def enable(self, args):
        self.label.enable(args)

    def disable(self, args):
        self.label.disable(args)

    def __init__(self, **kwargs):
        self.source = kwargs.pop('source', None)
        self.enaColor = kwargs.pop('enaColor', (0,1,0,1))
        self.padding_top = kwargs.pop('padding_top', 0)
        self.background_color = kwargs.pop('background_color', (1,0,0,1))
        self.text = kwargs.pop('text', "undefined text")
        self.id = kwargs.pop('id', "undefined id")
        self.imgWidth = kwargs.pop('imgWidth', 100)
        self.imgHeight = kwargs.pop('imgHeight', 100)
        self.widthParent = kwargs.pop('widthParent', None)
        self.isDir = kwargs.pop('isDir', False)
        self.user = kwargs.pop('user', None)

        #set the layout hight to fit the image height
        self.height = self.imgHeight + 2*self.padding_top
        self.size_hint_y= None

        super(SelectListViewItem, self).__init__(**kwargs)

        self.filler = SelectLabelBg(
            size_hint_x = None,
            width=10,
            size_hint_y=None,
            height=self.imgHeight,
            id="-1",
            text_size = (0,0),
            background_color=self.fillerColor
        )
        self.add_widget(self.filler)

        if self.source:
            self.image = ImageBg(
                background_color=self.background_color,
                width=self.imgWidth,
                size_hint= (None, None),
                height=self.imgHeight,
                source=self.source
            )
            self.add_widget(self.image)



        labelWidth = self.widthParent-self.imgWidth-self.filler.width
        self.label = SelectLabelBg(
            background_color = self.background_color,
            text_size=(labelWidth-20,self.imgHeight),
            enaColor=self.enaColor,
            text=self.text,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=self.imgHeight,
            size_hint_x=None,
            width=labelWidth,
            id=self.id
        )


        self.add_widget(self.label)
        self.bind(width=self.resize)


class SelectListView(Select, ScrollView):
    tmp = []
    layout = None
    widgets = []
    startId = None
    wId = -1 # id of the currently selected entry
    dir = "down"
    enaColor = ObjectProperty((1,1,1,0.5))
    headerText = None
    header = None


    def enter(self, args):
        logging.info("SelectListView: enter callback triggered")

    def enable(self, args):
        if isinstance(args,dict):
            increment = args.pop('inc', True)
        else:
            increment = True

        if self.wId < len(self.widgets) - 1:
            if increment:
                self.wId = self.wId + 1

            self.widgets[self.wId].enable(None)
            self.scroll_to(self.widgets[self.wId])



            if self.wId > 0:
                self.widgets[self.wId-1].disable(args)

        # if self.wId < 0:
        #     self.wId = 1
        return False # never returns true as there nothing we need to do when we come to end of list


    def disable(self, args):
        if isinstance(args,dict):
            increment = args.pop('inc', True)
            disTop = args.pop('disTop', True)
        else:
            increment = True
            disTop = True

        if self.wId >= 1:


            self.widgets[self.wId].disable(None)

            if increment:
                self.wId = self.wId - 1

            self.widgets[self.wId].enable(None)
            self.scroll_to(self.widgets[self.wId])

        else:
            if disTop:
                self.widgets[self.wId].disable(None)

                if self.selectFirst:
                    self.wId = 0
                else:
                    self.wId = -1

            return True
            
        return False


    def delTopText(self):
        logging.debug("FileList: remove first entry and enable it ")
        self.widgets.pop(0)
        self.layout.clear_widgets()

        for wid in self.widgets:
            self.layout.add_widget(wid)

        self.wId = 0
        self.widgets[self.wId].enable(None)

    """
    This function can be used to add a widget to the top of the list. For this
    we firts have to remove all the children, add the new entry and then re-add
    the old children.
    """

    def addTopText(self, text, user, bgColor):
        self.layout.clear_widgets()

        self.widgets.insert(0, SelectListViewItem(
            enaColor=self.enaColor,
            source=None,
            background_color=bgColor,
            text=text,
            id="-1",
            imgWidth=0,
            imgHeight=40,
            widthParent=self.width,
            fillerColor=self.fillerColor,
            isDir=False,
            user = user
        ))

        for wid in self.widgets:
            self.layout.add_widget(wid)

        self.topTextVisible = True


        #self.wId = self.wId + 1
        #if self.wId == 0:
        #    self.wId = 1
        for wid in self.widgets:
            wid.disable(None)

        self.wId = 0
        self.widgets[self.wId].enable(None)


    def add(self, text, isDir):
        id = str(len(self.widgets) + self.startId)
        imgWidth, imgHeight = 0, 46 #image height defines the hight of the element

        if not self.showDirs and isDir:
            return

        source = None # source="./resources/img/empty.png"
        if isDir:
            source="./resources/img/dir.png"
            imgWidth, imgHeight = 46, 46


        bg = None
        if len(self.widgets) % 2 == 0:
            bg = self.itemColor0#(0.2,0.2,0.2,1)
        else:
            bg = self.itemColor1#(0.1,0.1,0.1,1)

        if not self.fillerColor:
            self.fillerColor = bg

        self.widgets.append(SelectListViewItem(
            enaColor=self.enaColor,
            source=source,
            background_color=bg,
            text=text,
            id=id,
            imgWidth=imgWidth,
            imgHeight=imgHeight,
            widthParent=self.width,
            fillerColor=self.fillerColor,
            isDir = isDir,
            )

        )

        self.layout.add_widget(self.widgets[-1])


    def update(self, widget, val):
        for item in self.layout.children:
            item.width = self.width


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

        self.widthParent =  kwargs.pop('widthParent', None)
        self.fillerColor =  kwargs.pop('fillerColor', None)
        self.headerText =  kwargs.pop('headerText', None)
        self.showDirs =  kwargs.pop('showDirs', True)
        self.selectFirst =  kwargs.pop('selectFirst', True)

        self.itemColor0 = kwargs.pop('itemColor0', (0.2,0.2,0.2,1))
        self.itemColor1 = kwargs.pop('itemColor1', (0.1,0.1,0.1,1))

        super(SelectListView, self).__init__(**kwargs)

        self.isSelectable = True

        if self.selectFirst:
            self.wId = 0
        else:
            self.wId = -1

        self.layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.size_hint_y=None
        self.height= Window.height-100

        self.add_widget(self.layout)
        self.bind(enaColor=self.changeColor)
        #self.bind(width=self.update)

    def changeColor(self, wid, value):
        self.widgets[self.wId].label.color = value



class PlaylistJsonList(SelectListView):
    def updateList(self, args):

        if args == None:
            logging.error("Thomas:----------- args =  %s" % str(args))
            return

        if "currentWidget" in args:
            tmp = args['currentWidget']
            text = tmp.widgets[tmp.wId].text
            logging.error("Thomas:----------- text = %s" % text)


            path = os.path.join(globals.config[os.name]['playlist']['rootdir'], text)
            with open(path) as playFile:
                data = json.load(playFile)

            self.layout.clear_widgets()
            self.wId = 0
            self.widgets = []

            for item in data:
                 self.add(data[item]['name'], False)


if __name__ == "__main__":
    class Main(App):
        def build(self):
            return SelectListViewItem(source="./resources/img/arrow.png", text="gurcken brot", imgWidth=50, imgHeigth=50,background_color=(0.3,0.3,0.3,1))# bg = (0.6,0.6,0.6,1))

    Main().run()
