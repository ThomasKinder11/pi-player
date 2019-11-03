import unittest
import time

import sys
sys.path.insert(0,'..')

from screensaver import ScreenSaver
import includes


class ScreenManagerTest():
    current = None

def simTime(myTime):
    return myTime / 2

class TestScreensaver(unittest.TestCase):
    screenmanager = ScreenManagerTest()
    blkScreen = "blackscreen"
    mainmenu = "main_menu"
    saver = ScreenSaver(screenmanager, blkScreen, mainmenu)
    tmp = 5#includes.config['settings']['screensaverTime']
    includes.config['settings']['screensaverTime'] = simTime(tmp)
    saver.timeStep = simTime(saver.timeStep)
    saver.saverTimeout = simTime(saver.saverTimeout)
    testCmd = ['starts', 'resetu', 'disabled', 'socke', 'stopp', 'starn']

    def setUp(self):
        pass




    def test_0_enable(self):
        self.assertFalse(self.saver.ena)
        self.assertFalse(self.saver.active)
        self.assertEqual(self.saver.saverTimeout, simTime(5))

        self.saver.enable()

        tmp = includes.config['settings']['screensaverTime']
        time.sleep(tmp + simTime(1))
        self.assertGreaterEqual(self.saver.idleCounter, tmp)

        self.assertTrue(self.saver.ena)
        self.assertTrue(self.saver.active)
        self.assertEqual(self.saver.screenManager.current, self.blkScreen)


    def test_1_reset(self):
        self.assertTrue(self.saver.ena)
        self.assertTrue(self.saver.active)
        self.assertEqual(self.saver.screenManager.current, self.blkScreen)

        self.saver.resetTime()
        time.sleep(simTime(0.5))


        self.assertTrue(self.saver.ena)
        self.assertFalse(self.saver.active)
        self.assertEqual(self.saver.screenManager.current, self.mainmenu)

    def test_2_start(self):

        self.saver.start(None)
        time.sleep(simTime(0.5))

        tmp = simTime(includes.config['settings']['screensaverTime']-0.5)

        self.assertTrue(self.saver.ena)
        self.assertTrue(self.saver.active)
        self.assertEqual(self.saver.screenManager.current, self.blkScreen)
        self.assertGreater(self.saver.idleCounter, tmp)

    def test_3_disable(self):

        self.saver.disable()
        time.sleep(simTime(0.5))

        self.assertFalse(self.saver.ena)
        self.assertFalse(self.saver.active)
        self.assertEqual(self.saver.screenManager.current, self.mainmenu)
        self.assertGreater(self.saver.idleCounter, simTime(1))

    def test_4_weirdCmds(self):
        time.sleep(simTime(10)) #make sure screen saver is active
        ena = self.saver.ena
        active = self.saver.active
        current = self.saver.screenManager.current
        idleCounter = self.saver.idleCounter

        cmd = None
        self.saver.ctrlQueue.put(cmd)
        time.sleep(simTime(1))

        self.assertEqual(self.saver.ena, ena)
        self.assertEqual(self.saver.active, active)
        self.assertEqual(self.saver.screenManager.current, current)
        self.assertGreater(self.saver.idleCounter,includes.config['settings']['screensaverTime'])

        for item in self.testCmd:
            cmd = {'cmd':item}
            self.saver.ctrlQueue.put(cmd)
            time.sleep(simTime(1))

            self.assertEqual(self.saver.ena, ena)
            self.assertEqual(self.saver.active, active)
            self.assertEqual(self.saver.screenManager.current, current)
            self.assertGreater(self.saver.idleCounter,includes.config['settings']['screensaverTime'])




if __name__ == "__main__":
    unittest.main()
