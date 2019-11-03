import os

if os.name == "posix":
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


		def _worker(self):
			while True:
				try:
					for key,mask in self.selector.select():
						device = key.fileobj
					for event in device.read():
						if event.type == 1:
							if event.value == 0:#key press
								print("release")
								#self.onRelease((evdev.ecodes.KEY[event.code],event.code))

							#elif event.value == 0:#key release
							else:
								try:
									scancodes = {}
									#print("press {}".format((evdev.ecodes.KEY[event.code],event.code)))
									scancodes[106] = "right"
									scancodes[105] = "left"
									scancodes[103] = "up"
									scancodes[108] = "down"
									scancodes[158] = "browser back"
									scancodes[115] = "volume up"
									scancodes[114] = "volume down"
									scancodes[113] = "volume mute"
									scancodes[28] = "enter"
									scancodes[27] = "+"
									scancodes[53] = "-"
									scancodes[50] = "m"
									self.onPress((event.code, scancodes[event.code]))
								except:
									logging.debug("keyHandler: unsupported key code = {}".format(event.code))

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
