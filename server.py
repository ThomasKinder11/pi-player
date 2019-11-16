import platform
import  http.server
import json
import logging

cmdCallback = None

def _cmdCallback(self, data):
    return cmdCallback(data)

class WebServer(http.server.BaseHTTPRequestHandler, object):

    def do_GET(self):
        self.send_response(404)

    def do_POST(self):
        logging.debug("WebServer: Received post request...")
        if 'content-length' not in self.headers:
            return self.send_response(404)

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        self._post_data = self.rfile.read(content_length)

        pd = json.loads(self._post_data)
        ret = _cmdCallback(None, pd)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(json.dumps(ret).encode())

#
# For Standalone testing only
#
class Main:
    def __init__(self):
        httpd = http.server.HTTPServer(('127.0.0.1', 12345), WebServer)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()

if (__name__ == "__main__"):
    logging.basicConfig(level=logging.DEBUG)
    Main()
