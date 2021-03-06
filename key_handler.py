import os
import sys
import asyncio
import evdev
from selectors import DefaultSelector, EVENT_READ
import threading
import logging

class KeyHandler():
	keyboards = []
	thread = None
	selector = None

	'''These keys are used to identify keyboards which can be usefull for our application'''
	supportedKeys = [
		'KEY_LEFT',
		'KEY_RIGHT',
		'KEY_UP',
		'KEY_DOWN'
	]

	def onPress(self, args):
		pass

	def onRelease(self, args):
		pass

	def _setScancodes(self):
		self.scancodes = {}
		self.scancodes[106] = "right"
		self.scancodes[105] = "left"
		self.scancodes[103] = "up"
		self.scancodes[108] = "down"
		self.scancodes[158] = "browser back"
		self.scancodes[115] = "volume up"
		self.scancodes[114] = "volume down"
		self.scancodes[113] = "volume mute"
		self.scancodes[28] = "enter"
		self.scancodes[27] = "+"
		self.scancodes[53] = "-"
		self.scancodes[50] = "m"


	def _worker(self):
		self._setScancodes()
		while True:
			try:
				for key,mask in self.selector.select():
					device = key.fileobj
				for event in device.read():
					if event.type == 1:
						if event.value == 0:#key released
							self.onRelease((evdev.ecodes.KEY[event.code],event.code))

						#elif event.value == 0:#key pressed
						else:
							try:
								self.onPress((event.code, self.scancodes[event.code]))
							except AttributeError as e:
								logging.error("keyHandler: {}".format(e))
							except TypeError as e:
								logging.error("keyHandler: {}".format(e))
							except KeyError as e:
								logging.error("keyHandler: {}".format(e))
							except:
								logging.debug("keyHandler: [unhandled exception] unsupported key code = {}".format(event.code))

			except BlockingIOError:
				pass

	def __init__(self):
		devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

		for dev in devices:
			cap = dev.capabilities(verbose=True)
			for item in cap:
				if 'EV_KEY' in item:
					isKeyboard = False
					for availKeys in cap[item]:

						for supKey in self.supportedKeys:
							if supKey in availKeys[0]:
								isKeyboard = True
								break

						if isKeyboard:
							isKeyboard = False
							self.keyboards.append(dev)
							break

		self.selector = DefaultSelector()

		for kbd in self.keyboards:
			self.selector.register(kbd, EVENT_READ)

			self.thread = threading.Thread(target=self._worker)
			self.thread.setDaemon(True)
			self.thread.start()



#------------------------------------------------------------------------------
#
if __name__ == "__main__":

	def onPress(self, args):
		print(args)


	k = KeyHandler()
	k.onPress = onPress


	while True:
		import time
		time.sleep(2)
		print("alive")
