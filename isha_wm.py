import Xlib
import Xlib.display

import logging
import time

class IshaWm():
    displayWidth = None
    displayHeight = None
    display = None
    root = None
    activeWindow = None
    first = True
    mainWin = None

    def __init__(self):
        #logging.basicConfig(level=logging.DEBUG)
        logging.warning("IshaWM: init called")

        self.display = Xlib.display.Display()
        self.root = self.display.screen().root
        self.displayWidth = self.root.get_geometry().width
        self.displayHeight = self.root.get_geometry().height
        self.root.change_attributes(event_mask = Xlib.X.KeyPressMask | Xlib.X.SubstructureRedirectMask)

        f = open("isha_wm.height", "w")
        f.write("{}".format(self.displayHeight))
        f.close()

        f = open("isha_wm.width", "w")
        f.write("{}".format(self.displayWidth))
        f.close()


    def handleEvents(self):
        if self.display.pending_events() > 0:
            event = self.display.next_event()  # Get next event from display
            logging.warning("IshaWM: event type = {}".format(event.type))
        else:
            return

        """
        When we receive mapping event, the first window is condiered main window,
        And we make sure we give keyboard focus always back to this even while
        playing video
        """
        if event.type == Xlib.X.MapRequest:
            logging.warning("IshaWM: map request received")

            if self.first:
                self.first = False
                self.mainWin = event.window
                event.window.configure(width=self.displayWidth, height=self.displayHeight, x=0, y=0)
                event.window.map()

            else:
                event.window.map()
            
                #Make sure we give focus back to main window
                tree = self.root.query_tree()
                for child in tree.children:
                    if child.get_wm_name() == "Main":
                        child.set_input_focus(Xlib.X.RevertToNone, Xlib.X.CurrentTime)


    def main(self):
        while True:

            time.sleep(0.5)
            self.handleEvents()


if __name__ == "__main__":
    logging.info("IshaWM: start window manager as standalone app...")
    IshaWm().main()
