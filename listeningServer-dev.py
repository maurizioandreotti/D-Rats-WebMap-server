#!/usr/bin/python3
# Import modules to read parameters launched at invocation
import sys
import optparse

# Import some info to print on the /status page
import mapserverversion
from mapserverversion import VERSION, NAME, DESCRIPTION, LONG_DESCRIPTION, AUTHORS, AUTHORS_EMAIL

# Without these it won't capture the Ctrl-C to quit execution and come back to terminal...
from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, Response, request
import werkzeug.serving
from flask_socketio import SocketIO, emit

from threading import Thread
import time
from time import gmtime, strftime
import subprocess

########## Logging
class log2file(object):
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)

    def flush(self):
        for f in self.files:
            f.flush()

##########################

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app)

@app.route("/status")
def mapstatus():
    htmlreply = """
    <html><head><title>D-Rats WebMap server extender</title></head>
    <body><h1>D-Rats WebMap server extender</h1>
    <ul>
    <li>Application name: %s</li>
    <li>Version %s</li>
    <li>Description %s</li>
    <li>Authors: %s</li>
    </ul>
    </body></html>
    """ % (VERSION, NAME, LONG_DESCRIPTION, AUTHORS)
    return htmlreply

@socketio.on('connect', namespace='/stream')
def handle_connect():
    print("Got a socket connection")

@socketio.on('disconnect', namespace='/stream')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('message', namespace='/stream')
def handle_message(message):
    print("Received message: " + message)
    emit('message', message, broadcast=True)

def callback_gps(message):
    print("-------------------------------")
    print('callback_gps: issuing gpsfix: ', message)
    # Here we send the updated position to all the connected internet browser clients
    socketio.emit('message', message, namespace='/stream')

class MapServer(Thread):
    def __init__(self, port, lat, lng):
        self.port = port
        self.lat = lat # FIXME: THIS is not really used later on
        self.lng = lng # FIXME: THIS is not really used later on
        super(MapServer, self).__init__()

    def run(self):
        print("Mapserver: Starting HTTP map server on port: ", self.port)
        try:
            socketio.run(app, host='0.0.0.0', port=self.port)
        except Exception as e:
            print(f"Failed to start server on port {self.port}. Error: {e}")

####### Listening server ###########
# Modules for listening server
import socket
from _thread import start_new_thread

def clientthread(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            print('DISCONNECTED')
            break
        print('RECEIVED: ' + str(data))
        reply = 'OK...' + data.decode()
        if not data:
            break
        conn.sendall(reply.encode())
        callback_gps(data.decode())
        print("broadcast data: ", data.decode())
    conn.close()

class ListenServer(Thread):
    def __init__(self, host, port):
        super(ListenServer, self).__init__()
        self.host = host
        self.port = port

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('Socket for listening GPS fixes created')
        attempt = 0
        while attempt < 5:
            try:
                s.bind((self.host, self.port))
                break
            except socket.error as msg:
                print(f'Bind failed. Error: {msg}')
                if msg.errno == 98:
                    print(f"Port {self.port} is already in use. Retrying...")
                    attempt += 1
                    time.sleep(5)
                else:
                    sys.exit()
        s.listen(10)
        print(f'Socket bound to {self.host}:{self.port}, now listening')

        while True:
            conn, addr = s.accept()
            print('Connected with ' + addr[0] + ':' + str(addr[1]))
            start_new_thread(clientthread, (conn,))

def check_port_usage(port):
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stdout:
            print(f"Processes using port {port}:\n{result.stdout}")
        else:
            print(f"No processes are using port {port}.")
    except FileNotFoundError:
        print("The 'lsof' command is not available on this system.")

###############################################################################
if __name__ == "__main__":
    f = open('Log' + strftime("%Y-%m-%d-%H-%M-%S", gmtime()) + '.txt', 'w')
    original = sys.stdout
    sys.stdout = log2file(sys.stdout, f)

    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    print("Mapserver: processing __main__ section ")

    parser = optparse.OptionParser()
    parser.add_option('-o', '--outputPort', dest='outputPort', help='Port where to put the HTTP map server', default=8010, type=int)
    parser.add_option('-i', '--inputPort', dest='inputPort', help='Port where to receive GPS fix', default=8011, type=int)
    parser.add_option('-m', '--htmlpagename', dest='htmlpagename', help='HTML page template to serve to internet clients', default="map.html")
    parser.add_option('-x', '--lat', dest='initlat', help='initial latitude -- attention: this gets overridden if KMZ file is specified into the map template', default=45.85417259484529, type='float')
    parser.add_option('-y', '--lng', dest='initlng', help='initial longitude -- attention: this gets overridden if KMZ file is specified into the map template', default=9.388961847871542, type='float')
    (options, args) = parser.parse_args()

    listeningserverport = options.inputPort
    print("Listening server- port:", listeningserverport)
    
    mapserverport = options.outputPort
    print("Mapserver port:", mapserverport)
    
    htmlpagename = options.htmlpagename
    print("htmlpagename: ", htmlpagename)

    initlat = options.initlat
    initlng = options.initlng
    print("initlat: ", initlat)
    print("initlng: ", initlng)

    @app.route("/")
    def map(lat=initlat, lng=initlng):
        print("position:", lat, " - ", lng)
        return render_template(htmlpagename, lat=lat, lng=lng)

    mapserverrun = MapServer(mapserverport, initlat, initlng)
    listenserverrun = ListenServer('', listeningserverport)

    mapserverrun.start()
    listenserverrun.start()
