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

# THIS PROGRAM IMPLEMENTS A PROGRAM TO CALL THE MAPSERVER WITH 
# SIMULATED GPS POSITIONS 
# 
#
# Definitions
#
# gps fix: are the coordinates coming from the gps units via the radio
# points: are the positions to show on the map


#import modules to read parameters launched at invokation
import sys
import optparse
import time
from threading import Thread
import socket   #for sockets
from time import gmtime, strftime

initlat = 45.85417259484529 # FIXME: THIS SHOULD BE PASSED WHEN INVOKING THE HTTP SERVER
initlng = 9.388961847871542 # FIXME: THIS SHOULD BE PASSED WHEN INVOKING THE HTTP SERVER

#paramters of the server to call
host = "localhost" 
#host="192.168.0.11"
port= 5011

class FixServer(Thread):
   def __init__(self):
      super(FixServer, self).__init__()
   
   def run(self):
    ## if __name__ == "__main__":
         print " Mapserver: FixServer: Starting gpsfix generator server for testing purposes..."
         loop_fix()


#
###
######
##########
##############


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
   print 'Preparing gpsfix: ', point, station, comments
   
   # Prepare string to broadcast to internet browsers clients
   message = '{ "lat": "%f", "lng": "%f", "station": "%s", "comments": "%s","timestamp": "%s" }' % (point.lat, point.lng, station, comments, strftime("%Y-%m-%d %H:%M:%S", gmtime()))
 
   try:
      #create an AF_INET, STREAM socket (TCP)
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   except socket.error, msg:
      print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
      sys.exit();
   print 'Socket Created'   
   
   #Connect to remote server
   print "connecting to: ", host, ":",  port
   s.connect((host , port))
    
   print 'Socket Connected to ' + host
    
   #Send some data to remote server
   print "message to send:", message
    
   try :
      #Set the whole string
      s.sendall(message)
      s.close
   except socket.error:
      #Send failed
      print 'Send failed'
      sys.exit()
    
   print 'Message sent successfully'
    
   #Now receive data
   reply = s.recv(4096)
   print reply

#######
####
##
#

def loop_fix(lat=initlat, lng=initlng):
   #this is to generate sample gps-fixes
   #storing initial data
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



if __name__ == "__main__":
   print "GPSFixClientStub: processing __main__ section "
   fixserverrun = FixServer()
   fixserverrun.start()

  
