from multiprocessing.connection import Client, Listener
import pickle
import json
import sys
import logging

class Ipc():
    def sendCmd(self, cmd, port):
        address = ('localhost', port)
        conn = Client(address, authkey=b'secret password')
        conn.send(json.dumps(cmd))
        conn.close()

    def serverInit(self, port):
        address = ('localhost', port)     # family is deduced to be 'AF_INET'
        self.listener = Listener(address, authkey=b'secret password')

    def serverClose(self):
        self.listener.close()

    def serverGetCmd(self):
        conn = self.listener.accept()
        msg = conn.recv()
        data = json.loads(msg)
        return data


#
# Standalone test, not a real application
#
if __name__ == "__main__":
    ipc = Ipc()

    if sys.argv[1] == 's':#server
        ipc.serverInit(60005)
        while True:
            logging.error(ipc.serverGetCmd())


    elif sys.argv[1] == 'c':#client
        if len(sys.argv) >= 3:
            ipc.sendCmd({'cmd':sys.argv[2]}, 60005)
        else:
            ipc.sendCmd({'cmd':'thomas'}, 60005)


    else:
        sys.exit(-1)
