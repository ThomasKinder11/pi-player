import logging
import os
import time

import includes
from kivy.uix.stacklayout import StackLayout
from dialog import DialogHandler, DialogButtons
from selectable_items import SelectLabelBg


class MenuSystem(StackLayout):
    def callbackPlayfile(self, args):
        pass

    def _autoReplay(self, id):

        logging.error("Thmasßßßßßßßßßßßßßß: id = {}".format(id))
        tmp = {
            'path':includes.db['mediaPath'],
            'start':includes.db['runtime']
        }
        
        self.callbackPlayfile(tmp)
        self.handler._removeDialog(id)


    def _reboot(self, args):
        logging.error("TODO: reboot the system")
        os.system("/sbin/reboot")

    def _shutdown(self, args):
        logging.error("TODO: shutdown the system")
        os.system("/sbin/poweroff")

    def __init__(self, **kwargs):
        super(MenuSystem, self).__init__(**kwargs)

        btnDesc = [
            {
                'imgPath':'small_off',
                'callback':self._shutdown
            },
            {
                'imgPath':'small_reboot',
                'callback':self._reboot
            },

        ]

        color = includes.colors['black']
        self.divider = SelectLabelBg(
            background_color=color,
            height=5,
            size_hint_y=None
        )
        self.add_widget(self.divider)


        self.btn = DialogButtons(
            bgColor=includes.colors['black'],
            buttonDesc=btnDesc,
            size_hint_y=None,
            height=37.5
        )

        self.add_widget(self.btn)

        self.divider1 = SelectLabelBg(
            background_color=color,
            height=5,
            size_hint_y=None
        )
        self.add_widget(self.divider1)


        self.handler = DialogHandler()

        if includes.db['runtime'] != 0:
            btnDesc = [
                {
                    'imgPath':'small_play',
                    'callback':self._autoReplay
                }
            ]

            headerText = "System crashed"

            timeText = time.strftime('%H:%M:%S', time.gmtime(includes.db['runtime']))
            text = "System crashed while playing a video file\n"
            text += "Timestamp = {}".format(timeText)

            self.handler.addWarning(
                text=text,
                headerText=headerText,
                height=90,
                btnDesc= btnDesc
            )


        #self.handler.addInfo(text="This is the content for two", headerText="Second header", height=45)
        #self.handler.addError(text="This is the content for three", headerText="Third header", height=45)
        self.add_widget(self.handler)
