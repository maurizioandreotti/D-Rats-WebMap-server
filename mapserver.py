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

# Module description
#
# This module starts a webserver on given port which
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

#import some info to print in the /status page
import version
from version import VERSION, NAME, DESCRIPTION, LONG_DESCRIPTION, AUTHORS, AUTHORS_EMAIL


print "Mapserver module imported"


#--- parameters to feed into flask app ---
#
# htmlpagename: the html page to send to the internet browsers clients
htmlpagename = "map.html"
# lat, lng: set the initial coordinated where the map mage gets located at startup
initlat = 45.85417259484529 # FIXME: THIS SHOULD BE PASSED WHEN INVOKING THE HTTP SERVER
initlng = 9.388961847871542 # FIXME: THIS SHOULD BE PASSED WHEN INVOKING THE HTTP SERVER


#without these it wont't capture the ctrl-c to quit execution and come back to terminal...
from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, Response, request
import werkzeug.serving
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.server import SocketIOServer

from threading import Thread
import sys

import time

class FixServer(Thread):
    def __init__(self):
       super(FixServer, self).__init__()

    def run(self):
     ## if __name__ == "__main__":
          print " -- mapserver: FixServer: Starting gpsfix generator server for testing purposes..."
          loop_fix()

app = Flask(__name__)

@app.route("/")
def map(lat=initlat, lng=initlng):
  return render_template(htmlpagename, lat=lat, lng=lng)

@app.route("/status")
def mapstatus():
  htmlreply = """
  <html><head><title>D-Rats map server</title></head>
  <body><h1>D-Rats map server</h1>
   <ul>
   <li>Application name: %s</li>
   <li>Version %s</li>
   <li>Description  %s</li>
   <li>Authors: %s</li>
   
   </ul>
   </body></html>
  """ % (DRATS_VERSION, DRATS_NAME, DRATS_LONG_DESCRIPTION, AUTHORS )
  
  
  return htmlreply


@app.route("/socket.io/<path:rest>")
def stream(rest):
  try:
    socketio_manage(request.environ, {'/stream': StreamNamespace}, request)
  except:
    app.logger.error(" -- mapserver: app.route: Exception while handling socketio connection", exc_info=True)
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
      ws.emit(event, message)

class LatLng:
  # this class formats the gps fix
  def __init__(self, lat, lng):
    self.lat = float(lat)
    self.lng = float(lng)
  def __str__(self):
    return "Lat: %f, Lng: %f" % (self.lat, self.lng)


def callback_gps(lat, lng, station="", comments=""):
  # this class broadcasts the gps fixes to the web browsers
  point = LatLng(lat, lng)
  # this is for debugging the points sent to the client
  print ' -- mapserver: issuing gpsfix: ', point, station, comments
  # here we send the updated position to all the connected internet browsers clients
  StreamNamespace.broadcast('message', '{ "lat": "%f", "lng": "%f", "station": "%s", "comments": "%s" }' % (point.lat, point.lng, station, comments))


def loop_fix(lat=initlat, lng=initlng):
  #this is to generate sample gps-fixes
  lata=lat
  lnga=lng
  INTERVAL = 1
  x=1
  while True:
    # swap latlng every INTERVAL seconds
    if x % 2 :
      lat += .0001
      lng += .0001
      callback_gps(lat, lng, "zz001", x)
    else:
      lata -= .0001
      lnga -= .0001
      callback_gps(lata, lnga, "AA", comments="maurizio")
    x+=1
    time.sleep(1)
    #if x > 10:
       #break

class MapServer(Thread):
    def __init__(self, port, lat, lng):
        self.port = port
        self.lat = lat # FIXME: THIS is not really used later on
        self.lng = lng # FIXME: THIS is not really used later on
        super(MapServer, self).__init__()

    def run(self):
        print " -- mapserver: Starting http map server on port: ", self.port
        SocketIOServer(('0.0.0.0', self.port), app, resource="socket.io").serve_forever()
        #SocketIOServer(('', self.port), app, resource="socket.io").serve_forever()
        time.sleep(0.25)

#@werkzeug.serving.run_with_reloader
#def run_map_server():
#      app.debug = True
#      print " -- mapserver: Starting http map server on port: ", mapserverport
#      SocketIOServer(('', mapserverport), app, resource="socket.io").serve_forever()
#      time.sleep(0.25)


if __name__ == "__main__":

  print " -- mapserver: processing __main__ section "

  # Parameters to locate the define which map show at beginning
  # mapserver parameters


  # mapserverport: TCP port where to put the mapserver
  mapserverport = 5010

  #start the map server process - the lat,lng point defines where to point the initial map
  # - when invoked from  D-rats, this should passed from the gps position defined in the preferences
  mapserverrun = MapServer(mapserverport, initlat, initlng) # FIXME: initlat and initlng CAN BE PASSED IN THE FUCNTION BUT ARE NOT YET IMPLEMENTED
  fixserverrun = FixServer()

  mapserverrun.start()
  fixserverrun.start()
  ##mapserverrun.join()

  ##run_map_server()
  ##fixserverrun.join()

 # sys.exit(status)

