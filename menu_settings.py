import sys
import logging
from kivy.uix.gridlayout import GridLayout
from kivy.app import App

from selectable_items import SelectSlider, SelectButton
import includes

class MenuSettings(GridLayout):
    widgets = []
    widName = []
    btnOff = None

    def saveSettings(self, args):
        includes.config['settings']['screensaverTime'] = self.widgets[0].slider.value
        includes.config['settings']['osdTime'] = self.widgets[1].slider.value
        includes.writeConfig()

    def myexit(self, args):
        App.get_running_app().stop()

    def __init__(self, **kwargs):
        super(MenuSettings, self).__init__(**kwargs)

        self.cols = 1
        #self.rows = 2

        screensaverTime = includes.config['settings']['screensaverTime']
        osdTime = includes.config['settings']['osdTime']

        self.widgets.append(SelectSlider(
            value=screensaverTime,
            size_hint=(None, None),
            text="Screensaver time",
            enaColor=includes.styles['enaColor0'],
            id="100"
        ))

        self.widgets.append(SelectSlider(
            value=osdTime,
            size_hint=(None, None),
            text="OSD auto turnoff time",
            enaColor=includes.styles['enaColor0'],
            id="101"
        ))

        self.btnSave = SelectButton(
            text="Store",
            size_hint=(None, None),
            enaColor=includes.styles['enaColor0'],
            id="102"
        )

        self.btnOff = SelectButton(
            text="Sys.exit()",
            size_hint=(None, None),
            enaColor=includes.styles['enaColor0'],
            id="103"
        )

        self.btnSave.on_press = self.saveSettings
        self.btnSave.size_hint_y = None
        self.btnSave.height = 50

        self.widgets.append(self.btnSave)

        self.btnOff.on_press = self.myexit
        self.btnOff.size_hint_y = None
        self.btnOff.height = 50

        self.widgets.append(self.btnOff)

        for item in self.widgets:
            self.add_widget(item)
