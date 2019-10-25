import globals
from kivy.app import App
import kivy
from kivy.utils import get_color_from_hex as hexColor
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from select_listview import *
from menu_video import *
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color, Line

class MenuPlaylist(StackLayout, Select):
    _FILE_LIST = 0
    _JSON_LIST = 1
    mode = _FILE_LIST # mode 0 = json file fiew is selected, mode = 1 the list view of files in json are selected
    select = "json"



    def enable(self, args):#down


        if self.mode == self._FILE_LIST  and len(self.fileList.widgets) > 0:
            logging.info("enable/down")

            id = self.fileList.wId + 1

            if id == len(self.fileList.widgets):
                id = id - 1

            self.updateJsonFiles(self.fileList.widgets[id].text)
            self.fileList.enable(None)

            return False

        elif self.mode == self._JSON_LIST:


            self.files.enable(None)
            return False

    def disable(self,args):#up

        if self.mode == self._FILE_LIST and len(self.fileList.widgets) > 0:
            logging.info("disable/up")

            id = self.fileList.wId - 1
            if id < 0:
                id = 0


            self.updateJsonFiles(self.fileList.widgets[id].text)
            self.fileList.disable(None)
            return

        elif self.mode == self._JSON_LIST:
            self.files.disable(None)
            return False

    def left(self, args):
        logging.debug("MenuPlayList: left called...")

        if self.mode == self._FILE_LIST:

            return True
        elif self.mode == self._JSON_LIST:
            self.mode = self._FILE_LIST

            for wid in self.files.widgets:
                wid.disable({'inc':False})
            self.files.wId = 0

            #self.fileList.enaColor = (1,0,0,1)
            tmpID = self.fileList.wId
            self.fileList.widgets[tmpID].label.color = self.fileList.enaColor
        pass

    def right(self,args):
        logging.info("rigth")
        #self.fileList.widgets[0].enaColor = [1,0,0,1]
        if self.mode == self._FILE_LIST and len(self.fileList.widgets) > 0:
            self.mode = self._JSON_LIST
            self.files.enable({'inc':False})

            tmpID = self.fileList.wId
            self.fileList.widgets[tmpID].label.color = [1,0.5,0.2,1]
        elif self.mode == self._JSON_LIST:
            pass





    def updateJsonFiles(self, text):
        path = os.path.join(globals.config[os.name]['playlist']['rootdir'], text)

        if os.path.isdir(path):
            return

        with open(path) as playFile:
            data = json.load(playFile)

        self.files.layout.clear_widgets()
        self.files.wId = 0
        self.files.widgets = []

        for item in data:
             self.files.add(data[item]['name'], False)

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id', None)
        self.screenmanager = kwargs.pop('screenmanager', None)
        super(MenuPlaylist,self).__init__(**kwargs)

        self.cols = 2
        self.rows = 2
        # self.padding = 0

        columnWidth0 = Window.width * 0.3
        columnWidth1 = Window.width-columnWidth0
        headerHeight = 20
        headerText0 = "[b]Playlists[/b]"
        headerText1 = "[b]Media Files[/b]"

        headerColor0 = hexColor('#5a5560')#
        headerColor1 = hexColor('#2d4159')#(0.5,0.5,0,1)

        enaColor0 = [0.5,0.5,1,1]
        enaColor1 = [1,0.5,0.2,1]

        self.header0 = self.header = SelectLabelBg(
            background_color = headerColor0,
            text_size=(columnWidth0-20,headerHeight),
            text=headerText0,
            halign="center",
            valign="middle",
            size_hint_y=None,
            size_hint_x=None,
            height=headerHeight,
            width=columnWidth0,
            id="-1",
            markup = True
        )
        self.add_widget(self.header0)

        self.header1 = self.header = SelectLabelBg(
            background_color = headerColor1,
            text_size=(columnWidth0-20,headerHeight),
            text=headerText1,
            halign="center",
            valign="middle",
            size_hint_y=None,
            size_hint_x=None,
            height=headerHeight,
            width=columnWidth1,
            id="-1",
            markup = True
        )

        self.add_widget(self.header1)



        self.fileList = FileList(
            id=str(int(self.id)+1),
            rootdir=globals.config[os.name]['playlist']['rootdir'],
            enaColor=enaColor0,
            bar_width=10,
            size_hint_x=None,
            width=columnWidth0,
            supportedTypes=globals.config[os.name]['playlist']['types'],
            screenmanager=self.screenmanager,
            fillerColor=headerColor0,
            showDirs=False
        )

        self.files = PlaylistJsonList(
            id=str(int(self.id) + 5000),
            enaColor=enaColor1,
            bar_width=10,
            size_hint_x=None,
            width=columnWidth1,
            fillerColor=headerColor1,
        )


        #TODO: This code make a problem if directory does not contain any json files.
        #FileView also lising other files it seems....... Check this out why.


        self.add_widget(self.fileList)
        self.add_widget(self.files)

        self.mode = self._FILE_LIST

        #Fill the select List View with elements from the first json file
        for item in self.fileList.widgets:
            if "..." in item.text:
                continue
            elif item.text.endswith('.json'): #TODO this is not nicely implemented,
                self.updateJsonFiles(item.text)

        # if len(self.fileList.widgets) > 0:
        #     self.updateJsonFiles(self.fileList.widgets[0].text)
