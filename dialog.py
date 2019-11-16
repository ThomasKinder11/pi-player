import logging
from subprocess import threading

from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color

from selectable_items import SelectLabelBg, SelectButton, Select
import includes


class DialogCommon():
    dialog = None
    btnText = []
    btnClose = None
    btnCallbacks = []
    id = -1
    hId = 0

    def enable(self, args):
        self.dialog.enable(args)

    def disable(self, args):
        self.dialog.disable(args)

    def enter(self, args):
        self.dialog.enter(self.id)

    def left(self, args):
        self.dialog.left(args)

    def right(self, args):
        self.dialog.right(args)

    def __init__(self, id):
        self.id = id

class ErrorDialog(DialogCommon, Select):
    def __init__(self, text, headerText, height, closeCallback, id):
        super(ErrorDialog, self).__init__(id)

        buttonDesc = [
            {
                'imgPath':'close',
                'callback':closeCallback
            }
        ]


        self.dialog = Dialog(
            borderHeight=includes.styles['dialogBorderHeight'],
            headerHeight=40,
            contentHeight=height,
            headerColor=includes.colors['errMsgHead'],
            contentColor=includes.colors['errMsgContent'],
            sidebarColor=includes.colors['errMsgSidebar'],
            textColor=includes.colors['errMsgText'],
            text=text,
            headerText=headerText,
            buttonDesc=buttonDesc
        )


class WarningDialog(DialogCommon, Select):
    def __init__(self, text, headerText, height, id, buttonDesc, closeCallback):
        super(WarningDialog, self).__init__(id)

        btn = [
            {
                'imgPath':'close',
                'callback':closeCallback
            }
        ]

        btn = btn + buttonDesc
        logging.error("Dump: {}".format(btn))

        self.dialog = Dialog(
            borderHeight=includes.styles['dialogBorderHeight'],
            headerHeight=40,
            contentHeight=height,
            headerColor=includes.colors['warnMsgHead'],
            contentColor=includes.colors['warnMsgContent'],
            sidebarColor=includes.colors['warnMsgSidebar'],
            textColor=includes.colors['warnMsgText'],
            text=text,
            headerText=headerText,
            buttonDesc=btn
        )


#class InfoDialog(Select):
class InfoDialog(DialogCommon, Select):
    dialog = None
    id = -1
    headerText = None

    def __init__(self, text, headerText, height, closeCallback, id):
        buttonDesc = [
            {
                'imgPath':'close',
                'callback':closeCallback
            }
        ]

        self.id = id
        self.headerText = headerText
        #uper(InfoDialog, self).__init__(btnClose, id)
        self.dialog = Dialog(
            borderHeight=includes.styles['dialogBorderHeight'],
            headerHeight=40,
            contentHeight=height,
            headerColor=includes.colors['infoMsgHead'],
            contentColor=includes.colors['infoMsgContent'],
            sidebarColor=includes.colors['infoMsgSidebar'],
            textColor=includes.colors['infoMsgText'],
            text=text,
            headerText=headerText,
            buttonDesc=buttonDesc
        )



class DialogButtons(GridLayout):
    '''Each dialog can have upto 4 buttons as to control thes system
        like deleting a message, restarting a interrupted video or audio source.
    '''
    btnList = None
    callbackList = None
    bgColor = None
    back = None
    hId = -1
    user = None

    def enter(self, args):
        self.callbackList[self.hId](args)

    def enable(self, args):
        if self.hId < 0:
            self.hId = 0

        self.btnList[self.hId].enable(None)

    def disable(self, args):
        self.btnList[self.hId].disable(None)
        self.hId = -1


    def left(self, args):
        if self.hId != -1:
            self.btnList[self.hId].disable(None)

            self.hId = includes.clipInt(self.hId - 1, 0, len(self.btnList)-1)
            self.btnList[self.hId].enable(None)

    def right(self, args):
        if self.hId != -1:
            self.btnList[self.hId].disable(None)

        self.hId = includes.clipInt(self.hId + 1, 0, len(self.btnList)-1)
        self.btnList[self.hId].enable(None)

    def size_change(self, widget, value):
        #logging.error("Size change  value = {}".format(value))
        if self.back is not None:
            logging.error("Size change1")
            self.back.size = value

    def pos_change(self, widget, value):
        #logging.error("pos change  value = {}".format(value))
        if self.back is not None:
            logging.error("pos change1")
            self.back.pos = value

    def __init__(self, **kwargs):

        self.bgColor = kwargs.pop('bgColor', (1,1,1,1))
        buttonDesc = kwargs.pop('buttonDesc', [{}])

        #logging.error("Thomas:: kwargs = {}".format(kwargs))

        super(DialogButtons, self).__init__(**kwargs)
        self.rows = 1
        self.spacing = 5

        with self.canvas:
            Color(*self.bgColor)

            if self.parent is not None:
                tmpWidth = self.parent.width
            else:
                tmpWidth = Window.width

            size = (tmpWidth, self.height)
            self.back = Rectangle(size=size, pos=self.pos)

        #logging.error("thomas: Parent = {}".formatself.parent)
        self.btnList = []
        self.callbackList = []
        for node in buttonDesc:
            if len(buttonDesc) > 0 and node is not None:
                logging.error("THomas: noder found path = ./resources/img/{}".format(node['imgPath']))
                self.callbackList.append(node['callback'])
                self.btnList.append(
                    SelectButton(
                        #TODO: imgPath= "./resources/img/" + node['imgPath'],
                        imgPath= "atlas://resources/img/pi-player/" + node['imgPath'],
                        height=self.height,
                        size_hint_y=None,
                        size_hint_x=None,
                        width=100
                    )
                )

                self.add_widget(self.btnList[-1])


            else:
                return

        self.hId = -1

        self.bind(size=self.size_change)
        self.bind(pos=self.pos_change)


class Dialog(GridLayout):
    content = None
    sidebar = None
    headterText = None
    text = None
    cotentColor = None
    sidebarColor = None
    textColor = None
    btn = None
    contentColor = None
    sidebarColor = None
    textColor = None
    headerColor = None
    headerHeight = None
    contentHeight = None
    headerText = None
    text = None
    borderHeight = None
    sidebarWidth = None
    buttonDesc = None

    def enable(self, args):
        logging.error("ThomasDialog: btn = {}".format(self.btn))
        self.btn.enable(args)

    def disable(self, args):
        self.btn.disable(args)

    def enter(self, args):
        self.btn.enter(args)

    def right(self, args):
        logging.error("Dialog right called")
        self.btn.right(args)

    def left(self, args):
        self.btn.left(args)

    def __init__(self, **kwargs):
        self.contentColor = kwargs.pop('contentColor', (1, 1, 1, 1))
        self.sidebarColor = kwargs.pop('sidebarColor', (1, 1, 1, 1))
        self.textColor = kwargs.pop('textColor', (1, 1, 1, 1))
        self.headerColor = kwargs.pop('headerColor', (1, 1, 1, 1))
        self.headerHeight = kwargs.pop('headerHeight', 50)
        self.contentHeight = kwargs.pop('contentHeight', 100)
        self.headerText = kwargs.pop('headerText', "No header text")
        self.text = kwargs.pop('text', "No content text")
        self.borderHeight = kwargs.pop('borderHeight', 2)
        self.sidebarWidth = kwargs.pop('sidebarWidth', 40)
        self.buttonDesc = kwargs.pop('buttonDesc', None)

        super(Dialog, self).__init__()

        self.cols = 2

        if self.buttonDesc is not None:
            self.rows = 4
        else:
            self.rows = 3

        self.headerContent = SelectLabelBg(
            background_color=self.headerColor,
            text=self.headerText,
            size_hint=(1.0, None),
            height=self.headerHeight,
            color=self.textColor,
            valign="middle",
            halign="left"
        )

        self.sidebar = SelectLabelBg(
            background_color=self.sidebarColor,
            color=self.sidebarColor,
            text="a",
            size_hint=(None, None),
            width=self.sidebarWidth,
            height=self.headerHeight
        )


        #TODO: does this parent thing make actually sense?
        if self.parent is not None:
            tmpWidth = self.parent.width - self.sidebar.width
        else:
            tmpWidth = Window.width - self.sidebar.width - 20
        self.headerContent.text_size = (tmpWidth, self.headerHeight)

        #Row 2:
        self.sidebarContent = SelectLabelBg(
            background_color=self.sidebarColor,
            text="",
            size_hint=(None, None),
            width=self.sidebarWidth,
            height=self.contentHeight
        )

        self.content = SelectLabelBg(
            background_color=self.contentColor,
            text=self.text,
            color=self.textColor,
            halign="justify",
            valign="top",
            size_hint_y=None,
            height=self.contentHeight
        )

        #row 3
        self.border = SelectLabelBg(
            background_color=includes.colors['msgBorder'],
            size_hint_y=None,
            height=self.borderHeight,
        )

        self.sidebarBorder = SelectLabelBg(
            background_color=includes.colors['msgBorder'],
            text="",
            size_hint=(None, None),
            width=self.sidebarWidth,
            height=self.borderHeight
        )

        self.content.text_size = (tmpWidth, self.contentHeight - 20)

        self.size_hint_y = None
        self.height = self.headerHeight + self.contentHeight + self.border.height

        self.add_widget(self.sidebar)
        self.add_widget(self.headerContent)

        self.add_widget(self.sidebarContent)
        self.add_widget(self.content)

        if self.buttonDesc is not None:

            #logging.error("WarningDialog: We want buttons = {}".format(self.buttonDesc))

            self.sidebarBtn = SelectLabelBg(
                background_color=self.sidebarColor,
                text="",
                size_hint=(None, None),
                width=self.sidebarWidth,
                height=37.5
            )
            self.add_widget(self.sidebarBtn)
            #logging.error("Thomas Dialog:: slef.btn = {}".format(self.btn))
            self.btn = DialogButtons(
                buttonDesc=self.buttonDesc,
                bgColor=self.contentColor,
                size_hint_y=None,
                height=37.5
            )
            self.add_widget(self.btn)
            self.height = self.headerHeight + self.contentHeight + self.border.height + self.sidebarBtn.height

        self.add_widget(self.sidebarBorder)
        self.add_widget(self.border)


class DialogHandler(StackLayout, Select):
    dialogList = []
    wId = -1
    sema = None
    logfile = None

    def right(self, args):
        if self.wId >= 0 and len(self.dialogList) != 0:
            self.dialogList[self.wId].right(args)

    def left(self, args):
        if self.wId >= 0 and len(self.dialogList) != 0:
            self.dialogList[self.wId].left(args)

    def disable(self, args):

        logging.info("THomas: disable wId = {}".format(self.wId))
        if self.wId >= 0 and self.wId < len(self.dialogList):
            self.dialogList[self.wId].disable(args)
            self.wId = self.wId - 1
            self.wId = includes.clipInt(self.wId, -1, len(self.dialogList)-1)


            if self.wId >= 0:
                self.dialogList[self.wId].enable(args)



        logging.info("THomas: disable wId 2 = {}".format(self.wId))
        if self.wId < 0 or len(self.dialogList) == 0:
            self.wId = -1
            return True

        return False

    def enable(self, args):


        if len(self.dialogList) == 0:
            logging.info("THomas: dailog list is 0 = {}".format(self.wId))
            return True

        if self.wId < 0:
            self.wId = 0
            self.dialogList[self.wId].enable(args)

        elif self.wId >= 0 and self.wId < len(self.dialogList):
            self.dialogList[self.wId].disable(args)
            self.wId = self.wId + 1
            self.wId = includes.clipInt(self.wId, 0, len(self.dialogList)-1)
            self.dialogList[self.wId].enable(args)


        return False


    def enter(self, args):
        if self.wId >= 0 and self.wId <= len(self.dialogList) and len(self.dialogList) > 0:
            self.dialogList[self.wId].enter(args)

            if len(self.dialogList) == 0:
                return True

        return False

    def _updateView(self):
        self.clear_widgets()

        i = 0
        for widget in self.dialogList:
            widget.id = i
            i = i + 1
            self.add_widget(widget.dialog)

    def _removeDialog(self, dialogId):
        if len(self.dialogList) <= 0:
            logging.info("removeDialog: dialog list is empty")
            return

        widget = self.dialogList.pop(dialogId)

        self._updateView()
        for item in self.dialogList:
            item.disable(None)

        self.wId = includes.clipInt(self.wId - 1, 0, len(self.dialogList)-1)


        if len(self.dialogList) > 0:
            self.dialogList[self.wId].enable(None)


    def addInfo(self, text, headerText, height):
        info = InfoDialog(
            text=text,
            headerText=headerText,
            height=height, #TODO this should be calulated automatically accoriding to text size
            closeCallback=self._removeDialog,
            id=len(self.dialogList)
        )

        self.dialogList.append(info)
        self._updateView()
    #    self.wId = self.wId + 1


    def addWarning(self, text, headerText,height, btnDesc):
        warn = WarningDialog(
            text=text,
            headerText=headerText,
            height=height, #TODO this should be calulated automatically accoriding to text size
            closeCallback=self._removeDialog,
            id=len(self.dialogList),
            buttonDesc=btnDesc
        )

        self.dialogList.append(warn)
        self._updateView()

    def addError(self, text, headerText,height):
        err = ErrorDialog(
            text=text,
            headerText=headerText,
            height=height, #TODO this should be calulated automatically accoriding to text size
            closeCallback=self._removeDialog,
            id=len(self.dialogList)
        )

        self.dialogList.append(err)
        self._updateView()



    def __init__(self, **kwargs):
        super(DialogHandler, self).__init__(**kwargs)

        #self.cols = 1
        self.dialogList = []
        self.wId = -1

        self.sema = threading.Semaphore()


#
# Debug/Test application for manual testing
#
from kivy.app import App
from subprocess import threading
import time
class TestDialogButtons(App):
    widget = None

    def _taskThread(self):
        tSleep = 0.5

        time.sleep(2)
        for i in range(5):


            #Just enable the list, firts button should be highlighted
            self.widget.enable(None)
            time.sleep(tSleep)

            #move to next button on the right
            self.widget.right(None)
            self.widget.enter(None)
            time.sleep(tSleep)

            #enable the list a second time, this should not change anything
            self.widget.enable(None)
            time.sleep(tSleep)

            #move back to the first button
            self.widget.left(None)
            self.widget.enter(None)
            time.sleep(tSleep)

            #disable buttons
            self.widget.disable(None)
            time.sleep(tSleep)

        self.widget.enable(None)

        for i in range(5):
            self.widget.left(None)
            self.widget.enter(None)
            time.sleep(tSleep)

        for i in range(5):
            self.widget.right(None)
            self.widget.enter(None)
            time.sleep(tSleep)

        for i in range(5):
            self.widget.left(None)
            self.widget.enter(None)
            time.sleep(tSleep)


    def close(self, args):
        logging.error("TestDialogButtons: close button executed")

    def smallPlay(self, args):
        logging.error("TestDialogButtons: smallPlay button executed")

    def build(self):
        buttonDesc = [
            {
                'callback': self.close,
                'imgPath' : "close"
            },
            {
                'callback': self.smallPlay,
                'imgPath' : "small_play"
            }
        ]

        self.widget = DialogButtons(
            buttonDesc=buttonDesc,
            size_hint_y=None,
            height=37.5
        )

        self.thread = threading.Thread(target=self._taskThread)
        self.thread.setDaemon(True)
        self.thread.start()


        return self.widget

class TestInfoDialog(App):

    def build(self):
        widget = InfoDialog(headerText="Thomas", text="ich bin ein text", height=100, closeCallback=None, id=1)

        return widget.dialog


class DialogMain(App):
    '''This is just a Kivy app for testing the dialog widgets on its own'''
    def build(self):

        self.handler = DialogHandler()
        self.handler.addInfo(text="This is the content for one", headerText="First header", height=90)
        self.handler.addInfo(text="This is the content for two", headerText="Second header", height=45)
        self.handler.addInfo(text="This is the content for three", headerText="Third header", height=45)



        self.thread = threading.Thread(target=self._taskThread)
        self.thread.setDaemon(True)
        self.thread.start()

        # handler.enable(None)
        # handler.enable(None)
        # handler.enable(None)


        return self.handler


    def _taskThread(self):
        time.sleep(5)
        tSleep = 1

        #Enable first element and then disable
        logging.info("Test: Enable first and disable first")
        self.handler.enable(None)
        time.sleep(tSleep)

        self.handler.disable(None)
        time.sleep(tSleep)

        #Eneable first and second element and then disable only once --> 1st is enabled
        logging.info("Test: Enable first and secodn and disable second")
        self.handler.enable(None)
        time.sleep(tSleep)

        self.handler.enable(None)
        time.sleep(tSleep)

        self.handler.disable(None)
        time.sleep(tSleep)

        #enable 4 times even though we have only one three elements
        logging.info("Test: Enable 1,2,3 and 4,5 event though 4,5 not exits")
        self.handler.enable(None)
        time.sleep(tSleep)

        self.handler.enable(None)
        time.sleep(tSleep)

        self.handler.enter(None)
        time.sleep(tSleep)

        self.handler.disable(None)
        time.sleep(tSleep)

        self.handler.enter(None)
        time.sleep(tSleep)

        self.handler.enter(None)
        time.sleep(tSleep)

        self.handler.logfile.close()
        return

        # self.handler.enable(None)
        # time.sleep(tSleep)
        #
        # self.handler.enable(None)
        # time.sleep(tSleep)
        #
        # self.handler.enable(None)
        # time.sleep(tSleep)
        #
        # #disable three time to reset everything
        # logging.info("Test: Disable all again")
        # self.handler.disable(None)
        # time.sleep(tSleep)
        #
        # self.handler.disable(None)
        # time.sleep(tSleep)
        #
        # self.handler.disable(None)
        # time.sleep(tSleep)
        #
        # #disbale a few more times to check lower boundary  and enable once to select first element
        # logging.info("Test: A few more disables to test lower boundary")
        # self.handler.disable(None)
        # time.sleep(tSleep)
        #
        # self.handler.disable(None)
        # time.sleep(tSleep)
        #
        # self.handler.disable(None)
        # time.sleep(tSleep)
        #
        # self.handler.enable(None)
        # time.sleep(tSleep)




if __name__ == "__main__":
    DialogMain().run()
    #TestDialogButtons().run()
    #TestInfoDialog().run()
