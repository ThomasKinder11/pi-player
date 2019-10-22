from isha_pi_kivy import SelectableSlider

import kivy
from kivy.uix.gridlayout import GridLayout
import logging
import json
import globals

class MenuSettings(GridLayout):
    widgets = []
    widName = []

    def __init__(self, **kwargs):
        super(MenuSettings, self).__init__(**kwargs)

        self.cols = 1
        self.rows = 2

        screensaverTime = globals.config['settings']['screensaverTime']
        osdTime = globals.config['settings']['osdTime']

        self.widgets.append(SelectableSlider(value=screensaverTime, size_hint=(None,None), text="Screensaver time", enaColor=[0.5,0.5,1,1], id="100"))
        self.widgets.append(SelectableSlider(value=osdTime, size_hint=(None,None), text="OSD auto turnoff time", enaColor=[0.5,0.5,1,1], id="101"))

        for item in self.widgets:
            self.add_widget(item)
