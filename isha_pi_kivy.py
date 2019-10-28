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
from kivy.properties import ObjectProperty

import logging
from kivy.graphics import Color, Rectangle

class Select():
    selected = None
    type = None
    enaColor =  ObjectProperty()
    defaultColor = None
    isSelectable = True
    onEnter = None
    user = {}

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

    def enable(self, args):
        logging.warning("I AM NOT IMPLEMENTED self = {}".format(self))
    def disable(self, args):
        #raise NotImplementedError("disable function of Select class not implemented")
        logging.warning("I AM NOT IMPLEMENTED self = {}".format(self))





class SelectableTabbedPanelHeader(Select, TabbedPanelHeader):
    def enable(self, args):
        self.selected = True
        self.background_color = self.enaColor
        return True

    def disable(self, args):
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
    def enable(self, args):
        self.selected = True
        self.color = self.enaColor
        return True

    def disable(self, args):
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

    def on_press(self):
        pass

    def enable(self, args):
        self.selected = True

        if self.btnType == "text":
            self.color = self.enaColor

        elif self.btnType == "image":
            self.background_normal = self.imgPath + "_select.png"

        return True

    def disable(self, args):
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

        if self.imgPath:
            self.btnType = "image"
            self.background_normal = self.imgPath + ".png"
        else:
            self.btnType = "text"

        super(SelectButton, self).__init__(**kwargs)

    


class SelectSlider(Select, GridLayout):
    label = None
    slider = None
    valLabel = None

    def enable(self, args):
        self.selected = True
        self.label.color = self.enaColor
        return True

    def disable(self, args):
        self.selected = False
        self.label.color = self.defaultColor
        return True

    def increment(self, args):
        val = self.slider.value

        if val == self.slider.max:
            return

        val = val + 1

        self.slider.value = val
        self.valLabel.text = str(val)+"s"

    def decrement(self, args):
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
        super(SelectSlider, self).__init__(**kwargs)

        self.label = Label(text=text, size_hint=(None,None), width=200, height=50)
        self.slider = Slider(min=-0, max=20, value=self.value,  size_hint=(None,None), width=200, height=50)

        val = self.slider.value
        self.valLabel = Label(text=str(val)+'s', size_hint=(None,None), width=10, height=50)

        self.selected = False
        self.type = "selectslider"
        self.defaultColor = self.label.color

        self.rows = 1
        self.cols = 3


        self.add_widget(self.label)
        self.add_widget(self.slider)
        self.add_widget(self.valLabel)
