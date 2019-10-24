from isha_pi_kivy import SelectSlider, SelectButton

import kivy
from kivy.uix.gridlayout import GridLayout
import logging
import json
import globals

class MenuSettings(GridLayout):
    widgets = []
    widName = []
    def save_settings(self, args):
        globals.config['settings']['screensaverTime'] = self.widgets[0].slider.value
        globals.config['settings']['osdTime'] = self.widgets[1].slider.value
        globals.writeConfig()

    def __init__(self, **kwargs):
        super(MenuSettings, self).__init__(**kwargs)

        self.cols = 1
        #self.rows = 2

        screensaverTime = globals.config['settings']['screensaverTime']
        osdTime = globals.config['settings']['osdTime']

        self.widgets.append(SelectSlider(value=screensaverTime, size_hint=(None,None), text="Screensaver time", enaColor=[0.5,0.5,1,1], id="100"))
        self.widgets.append(SelectSlider(value=osdTime, size_hint=(None,None), text="OSD auto turnoff time", enaColor=[0.5,0.5,1,1], id="101"))

        self.btnSave = SelectButton(text="Store", size_hint=(None,None), enaColor=[0.5,0.5,1,1], id="102")
        self.btnSave.on_press = self.save_settings
        self.btnSave.size_hint_y=None
        self.btnSave.height=50

        self.widgets.append(self.btnSave)

        for item in self.widgets:
            self.add_widget(item)
