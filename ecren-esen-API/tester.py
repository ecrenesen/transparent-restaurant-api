


from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json

"""
restaurant API with http.server and json built-in python packages
by Ecren Esen

"""


data = {"Hello":"hello"}
hostName = "localhost"
serverPort = 8000

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            print(self.path)
            self.wfile.write(bytes(json.dumps(data,indent=4),"utf-8"))
        except:
            pass



if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
