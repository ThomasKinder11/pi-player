from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.slider import Slider
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

import logging
from kivy.graphics import Color, Rectangle

class Select():
    selected = None
    type = None
    enaColor = None
    defaultColor = None
    isSelectable = True

    # selectableWidgets = {}

    # def findSelectableChildren(self, children):
    #     if not children:
    #         return
    #
    #     for child in children:
    #         try:
    #             self.findSelectableChildren(child.children)
    #             if child and child.isSelectable:
    #                 self.selectableWidgets[int(child.id)] = child
    #         except:
    #             pass

    def enable(self):
        raise NotImplementedError("enable function of Select class not implemented")

    def disable(self):
        raise NotImplementedError("disable function of Select class not implemented")


class SelectListViewItem(StackLayout):
    layout = None
    label = None
    text = None

    def enable(self):
        self.label.enable()

    def disable(self):
        self.label.disable()

    def __init__(self, **kwargs):
        self.cols = 1
        self.rows = 1
        self.enaColor = kwargs.pop('enaColor', None)

        if not self.enaColor:
            logging.error("SelectListViewItem: enaColor not set")
            return

        self.text = kwargs.pop('text', "undefined")

        super(SelectListViewItem, self).__init__(**kwargs)
        logging.error("------------- self.pos = {} / self.size = {} / root.size =  / root.pos=".format(self.pos, self.size))# self.parent.size, self.parent.pos))


        self.label = SelectLabel(text=self.text, id=kwargs['id'], size_hint_x=None, width=400, halign="left", enaColor=self.enaColor)

        self.add_widget(self.label)

        logging.error("----------------- Text = {}".format(self.label.text))

        with self.canvas.before:
            Color(1, 0, 0, 0.1)
            Rectangle(pos=self.pos, size=self.size)


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
        logging.error("$$$$$$$$$$$$$$$$$$ wId = {} / wid cnt = {}".format(self.wId, len(self.widgets)))

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


    def add(self, text):
        id = str(len(self.widgets) + self.startId)

        bg = None
        if len(self.widgets) % 2 == 0:
            bg = (0.6,0.6,0.6,1)
        else:
            bg = (0.5,0.5,0.5,1)

        self.widgets.append(SelectButton(
                                            background_color=bg,
                                            text_size=(Window.width-30,15),
                                            halign="left",
                                            enaColor=self.enaColor,
                                            text=text,
                                            size_hint_y=None,
                                            height=30,
                                            id=id)
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


        # for i in range(100):
        #
        #     self.tmp.append(SelectLabel(size_hint_y=None, height=40, id="{}".format(20000+i),  text="Label {}".format(i)))
        #     self.layout.add_widget(self.tmp[-1])

        self.add_widget(self.layout)



class SelectableTabbedPanelHeader(Select, TabbedPanelHeader):
    def enable(self):
        self.selected = True
        self.background_color = self.enaColor
        return True

    def disable(self):
        self.selected = False
        self.background_color = self.defaultColor
        return True


    def __init__(self, **kwargs):
        self.enaColor = kwargs.pop('enaColor', None)

        super(SelectableTabbedPanelHeader, self).__init__(**kwargs)


        if not self.enaColor:
            self.enaColor =  self.background_color

        self.defaultColor = self.background_color
        self.selected = False
        self.type = "selectabletabbedpanelheader"


class SelectLabel(Label, Select):
    def enable(self):
        self.selected = True
        self.color = self.enaColor
        return True

    def disable(self):
        self.selected = False
        self.color = self.defaultColor
        return True

    def __init__(self, **kwargs):

        self.enaColor = kwargs.pop('enaColor', None)

        if not self.enaColor:
            self.enaColor = self.defaultColor

        super(SelectLabel, self).__init__(**kwargs)

        self.defaultColor = self.color
        self.selected = False
        self.type = "label"

        return


class SelectButton(Button, Select):
    btnType = None

    def enable(self):
        self.selected = True

        if self.btnType == "text":
            self.color = self.enaColor

        elif self.btnType == "image":
            self.background_normal = self.imgPath + "_select.png"

        return True

    def disable(self):
        self.selected = False

        if self.btnType == "text":
            self.color = self.defaultColor
        elif self.btnType == "image":
            self.background_normal = self.imgPath + ".png"
        #self.background_color = (0,0,0.5,1)
        return True

    def __init__(self, **kwargs):
        self.enaColor = kwargs.pop('enaColor', None)
        self.defaultColor = self.color

        if not self.enaColor:
            self.enaColor = (1,0,0,0.2)#self.defaultColor


        # background_down= "./resources/img/previous_select.png",
        self.imgPath = kwargs.pop('imgPath', None)
        logging.info("Btn: self.impPath = {}".format(self.imgPath))

        if self.imgPath:
            self.btnType = "image"
            self.background_normal = self.imgPath + ".png"
        else:
            self.btnType = "text"



        super(SelectButton, self).__init__(**kwargs)

        #self.bgDefault = self.background_color#
        self.background_disabled_down = "c"
        logging.debug("SelectButton: position is = {0}".format(self.pos))
        # with self.canvas.before:
        #     Color(1, 0, 0, 1)
        #     Rectangle(pos=self.pos, size=self.size)

class SelectableSlider(Select, GridLayout):
    label = None
    slider = None
    valLabel = None

    def enable(self):
        self.selected = True
        self.label.color = self.enaColor
        return True

    def disable(self):
        self.selected = False
        self.label.color = self.defaultColor
        return True

    def increment(self):
        val = self.slider.value

        if val == self.slider.max:
            return

        val = val + 1

        self.slider.value = val
        self.valLabel.text = str(val)+"s"

    def decrement(self):
        val = self.slider.value

        if val == self.slider.min:
            return

        val = val - 1

        self.slider.value = val
        self.valLabel.text = str(val)+"s"

    def __init__(self, **kwargs):

        #remove all kwargs argment which shall not be passed to child
        self.id = kwargs.pop('id', None)
        if not id:
            print("SelectSlider::init::id is not defined")
            return -1

        self.enaColor = kwargs.pop('enaColor', None)
        if not id:
            print("SelectSlider::init::enaColor is not defined")
            return -1

        self.value = kwargs.pop('value',None)


        text = kwargs.pop('text', "!!!Empty Name in slider!!!")

        #call super only after additional arguments have been popped
        super(SelectableSlider, self).__init__(**kwargs)

        self.label = Label(text=text, size_hint=(None,None), width=200, height=50)
        self.slider = Slider(min=-0, max=20, value=self.value,  size_hint=(None,None), width=200, height=50)

        val = self.slider.value
        self.valLabel = Label(text=str(val)+'s', size_hint=(None,None), width=10, height=50)

        self.selected = False
        self.type = "selectableslider"
        self.defaultColor = self.label.color

        self.rows = 1
        self.cols = 3


        self.add_widget(self.label)
        self.add_widget(self.slider)
        self.add_widget(self.valLabel)
