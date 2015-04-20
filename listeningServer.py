#!/usr/bin/python
#
# Copyright 2014 Maurizio Andreotti IZ2LXI - based on a work from Andrea Galbusera Gizero
#
# This program is free software: you can redistribute it and/or modify
# """module docstring"""it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Description
#
# This sw starts a webserver on given port which
#  - at first connections:
#      - returns an html page to the browsers which make the browsers
#        - load google map and
#        - keep connected to the webserver via ajax json script to get gps points
#        - diplay gps points on the map
#  - keeps sending (broadcasting) the gps points to the browsers
#
# Definitions
#
# gps fix: are the coordinates coming from the gps units via the radio
# points: are the positions to show on the map


#import modules to read parameters launched at invokation
import sys
import optparse

#import some info to print in the /status page
import mapserverversion
from mapserverversion import VERSION, NAME, DESCRIPTION, LONG_DESCRIPTION, AUTHORS, AUTHORS_EMAIL


#without these it wont't capture the ctrl-c to quit execution and come back to terminal...
#from gevent import monkey
#monkey.patch_all()

from flask import Flask, render_template, Response, request
import werkzeug.serving
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.server import SocketIOServer

from threading import Thread
import time

####### listening server ###########
#modules for listening server
import socket
#import sys
from thread import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket for listening gps fixes created'
       
            
############ http Mapserver ##################
#--- parameters to feed into flask app ---
#
# htmlpagename: the html page to send to the internet browsers clients
# the htmlpagename must be into the "templates" folder
htmlpagename = "map.html"
# lat, lng: set the initial coordinated where the map mage gets located at startup
initlat = 45.85417259484529 # FIXME: THIS SHOULD BE PASSED WHEN INVOKING THE HTTP SERVER
initlng = 9.388961847871542 # FIXME: THIS SHOULD BE PASSED WHEN INVOKING THE HTTP SERVER


################################################
#Listening server function for handling connections. This will be used to create threads
def clientthread(conn):
    #Sending message to connected client
     
    #infinite loop so that function do not terminate and thread do not end.
    while True:
         
        #Receiving from client
        data = conn.recv(1024)
        if not data:
            print('DISCONNECTED')
            break        
        print('RECEIVED: ' + str(data))
        reply = 'OK...' + data
        if not data: 
            break
        #not really necessary, but lets send back the data received 
        conn.sendall(reply)
        #let's now call the function to broadcast the message onm the map
        callback_gps(data)
        #StreamNamespace.broadcast('message', data)
        print "broadcast data: ", data
    #came out of loop
    conn.close()
            

class ListenServer(Thread):
    def __init__(self):
        #parameters 
        HOST = ''   # Symbolic name, meaning all available interfaces
        PORT = listeningserverport # Arbitrary non-privileged port
                 
        #Bind socket to local host and port
        try:
            s.bind((HOST, PORT))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
             
        print 'Socket bind complete on: ',HOST, ":", PORT
         
        #Start listening on socket
        s.listen(10)
        print 'Socket now listening'
        super(ListenServer, self).__init__()
        
    def run(self):
     ## if __name__ == "__main__":
        print " Mapserver: ListenServer: Starting "
        
        #now keep talking with the client
        while 1:
            #wait to accept a connection - blocking call
            conn, addr = s.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
             
            #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
            start_new_thread(clientthread ,(conn,))
         
        s.close()           

##########################

app = Flask(__name__)

@app.route("/")
def map(lat=initlat, lng=initlng):
  return render_template(htmlpagename, lat=lat, lng=lng)

@app.route("/status")
def mapstatus():
  htmlreply = """
  <html><head><title>D-Rats WebMap server extender</title></head>
  <body><h1>D-Rats WebMap server extender</h1>
   <ul>
   <li>Application name: %s</li>
   <li>Version %s</li>
   <li>Description  %s</li>
   <li>Authors: %s</li>
   </ul>
   </body></html>
  """ % (VERSION, NAME, LONG_DESCRIPTION, AUTHORS )
  return htmlreply


@app.route("/socket.io/<path:rest>")
def stream(rest):
    try:
        socketio_manage(request.environ, {'/stream': StreamNamespace}, request)
    except:
        app.logger.error("Mapserver: app.route: Exception while handling socketio connection", exc_info=True)
    return Response()

class StreamNamespace(BaseNamespace):
    sockets = {}
    def recv_connect(self):
        print "Got a socket connection"
        self.sockets[id(self)] = self
    def disconnect(self, *args, **kwargs):
        if id(self) in self.sockets:
            del self.sockets[id(self)]
        super(StreamNamespace, self).disconnect(*args, **kwargs)
    @classmethod
    def broadcast(self, event, message):
        for ws in self.sockets.values():
            print "emitting message to http clients: ", message
            ws.emit(event, message)


def callback_gps(message):
    print "-------------------------------"
    print 'callback_gps: issuing gpsfix: ', message
    # here we send the updated position to all the connected internet browsers clients
    StreamNamespace.broadcast('message', message)


class MapServer(Thread):
    def __init__(self, port, lat, lng):
        self.port = port
        self.lat = lat # FIXME: THIS is not really used later on
        self.lng = lng # FIXME: THIS is not really used later on
        super(MapServer, self).__init__()

    def run(self):
        print "Mapserver: Starting http map server on port: ", self.port
        SocketIOServer(('0.0.0.0', self.port), app, resource="socket.io").serve_forever()
        #SocketIOServer(('', self.port), app, resource="socket.io").serve_forever()
        time.sleep(0.25)
        
###############################################################################
if __name__ == "__main__":
    print "Mapserver: processing __main__ section "
    

    parser = optparse.OptionParser()
    parser.add_option('-o', '--outputPort', dest='outputPort', help='Port where to put the http map server', default="5010", type=int)
    parser.add_option('-i', '--inputPort', dest='inputPort', help='Port where to receive GPS fix', default="5011", type=int)
    
    (options, args) = parser.parse_args()
    
    # listeningserverport: TCP port where to listen the gps fixes
    listeningserverport = options.inputPort
    print "listenings erver: port:", listeningserverport
    
    
    # mapserverport: TCP port where to put the mapserver
    mapserverport = options.outputPort
    print "Mapserver: port:", mapserverport


    #start the map server process - the lat,lng point defines where to point the initial map
    mapserverrun = MapServer(mapserverport, initlat, initlng) 
    
    listenserverrun = ListenServer()
    
    mapserverrun.start()
    listenserverrun.start()

