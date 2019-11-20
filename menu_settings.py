import sys
import logging
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.app import App

from selectable_items import SelectSlider, SelectButton, Select, SelectCheckBox, SelectLabelBg
import includes

class MenuSettings(GridLayout, Select):
    widgets = []
    wId = -1
    widName = []
    btnOff = None

    def enable(self, args):
        self.wId = includes.clipInt(self.wId + 1, 0, len(self.widgets)-1)
        logging.debug("MenuSettings: enable fct called")
        self.widgets[self.wId].enable(None)

        if self.wId >= 1:
            self.widgets[self.wId-1].disable(None)

        return False

    def disable(self, args):


        logging.debug("MenuSettings: disable fct called")
        self.widgets[self.wId].disable(None)

        if self.wId >= 1:
            self.widgets[self.wId-1].enable(None)
        else:
            self.wId = -1
            return True

        self.wId = includes.clipInt(self.wId - 1, 0, len(self.widgets))
        return False

    def right(self, args):
        logging.debug("MenuSettings: right called")
        if self.widgets[self.wId].hasLeftRight:
            self.widgets[self.wId].right(None)


    def left(self, args):
        logging.debug("MenuSettings: left called")
        if self.widgets[self.wId].hasLeftRight:
            self.widgets[self.wId].left(None)

    def enter(self, args):
        logging.debug("MenuSettings: enter called, args = {} / wid = {}".format(args, self.wId))
        self.widgets[self.wId].enter(args)

    def _saveSettings(self, args):
        includes.config['settings']['screensaverTime'] = self.widgets[0].slider.value
        includes.config['settings']['osdTime'] = self.widgets[1].slider.value
        includes.writeConfig()

    def myexit(self, args):
        App.get_running_app().stop()

    def __init__(self, **kwargs):
        #self.id = kwargs.pop('id', "-1")

        super(MenuSettings, self).__init__(**kwargs)

        self.cols = 1
        #self.rows = 2

        screensaverTime = includes.config['settings']['screensaverTime']
        osdTime = includes.config['settings']['osdTime']

        self.widgets.append(SelectSlider(
            value=screensaverTime,
            size_hint=(1, None),
            text="Screensaver time",
            enaColor=includes.styles['enaColor0'],
            id="-1",
            fontSize=includes.styles['fontSize']
        ))

        self.widgets.append(SelectSlider(
            value=osdTime,
            size_hint=(1, None),
            text="OSD auto turnoff time",
            enaColor=includes.styles['enaColor0'],
            id="-1",
            fontSize=includes.styles['fontSize']
        ))

        self.btnSave = SelectButton(
            text="Save",
            size_hint=(None, None),
            enaColor=includes.styles['enaColor0'],
            id="-1",
            font_size=includes.styles['fontSize']
        )


        self.musicAutoplay = SelectCheckBox(
            text="Autostart Music",
            enaColor=includes.styles['enaColor0']
        )

        self.musicAutoplay.checkbox.active = includes.config['audio']['autoplay'] == 'true'

        self.musicAutoplay.size_hint_y = None
        self.musicAutoplay.height = 50
        self.widgets.append(self.musicAutoplay)

        self.videoAutoplay = SelectCheckBox(
            text="Autostart Video",
            enaColor=includes.styles['enaColor0']
        )
        self.videoAutoplay.checkbox.active = includes.config['video']['autoplay'] == 'true'

        self.videoAutoplay.size_hint_y = None
        self.videoAutoplay.height = 50
        self.widgets.append(self.videoAutoplay)

        self.headVideoAudio = SelectLabelBg(
            text="Video/Audio Settings",
            background_color=includes.colors['gray'],
            size_hint_y=None,
            height=35
        )

        self.headSystemSettings = SelectLabelBg(
            text="System Settings",
            background_color=includes.colors['gray'],
            size_hint_y=None,
            height=35
        )

        self.headSettingsCtrl = SelectLabelBg(
            text="Settings Controls",
            background_color=includes.colors['gray'],
            size_hint_y=None,
            height=35
        )


        self.btnSave.enter = self._saveSettings
        self.btnSave.size_hint_y = None
        self.btnSave.height = 50
        self.widgets.append(self.btnSave)

        for item in self.widgets:
            if item == self.musicAutoplay:
                self.add_widget(self.headVideoAudio)

            if item == self.widgets[0]:#first slider
                self.add_widget(self.headSystemSettings)

            if item == self.btnSave:
                self.add_widget(self.headSettingsCtrl)

            self.add_widget(item)





        self.wId = -1
