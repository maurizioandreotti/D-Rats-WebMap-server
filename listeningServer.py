#!/usr/bin/python3
import sys
import optparse
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import socket
import eventlet
import eventlet.wsgi
from eventlet.green import socket

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app, async_mode='eventlet')

@app.route("/")
def map():
    return render_template('map-osm.html')

@app.route("/status")
def mapstatus():
    return """
    <html>
    <head><title>D-Rats WebMap server extender</title></head>
    <body>
    <h1>D-Rats WebMap server extender</h1>
    <ul>
    <li>Application name: D-Rats WebMap server extender</li> 
    <li>Version: 1.0</li>
    <li>Description: Extender for D-Rats WebMap server</li>
    <li>Authors: Unknown</li>
    </ul>
    </body>
    </html>
    """

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
    print("callback_gps: issuing gpsfix: ", message)  # Debug log for GPS fix message
    socketio.emit('message', message, namespace='/stream')

def clientthread(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            print('Client DISCONNECTED')
            break
        print('RECEIVED: ' + str(data))  # Debug log for data received
        reply = 'OK...' + data.decode()
        conn.sendall(reply.encode())
        callback_gps(data.decode())
    conn.close()

def listen_server(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket for listening GPS fixes created')
    attempt = 0
    while attempt < 5:
        try:
            s.bind((host, port))
            break
        except socket.error as msg:
            print(f'Bind failed. Error: {msg}')
            if msg.errno == 98:
                print(f"Port {port} is already in use. Retrying...")
                attempt += 1
                eventlet.sleep(5)
            else:
                sys.exit()
    s.listen(10)
    print(f'Socket bound to {host}:{port}, now listening')

    while True:
        conn, addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        eventlet.spawn_n(clientthread, conn)

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-o', '--outputPort', dest='outputPort', help='Port where to put the HTTP map server', default=8010, type=int)
    parser.add_option('-i', '--inputPort', dest='inputPort', help='Port where to receive GPS fix', default=8011, type=int)
    (options, args) = parser.parse_args()

    listeningserverport = options.inputPort
    mapserverport = options.outputPort

    eventlet.spawn_n(listen_server, '', listeningserverport)

    print("Mapserver: Starting HTTP map server on port: ", mapserverport)
    try:
        eventlet.wsgi.server(eventlet.listen(('0.0.0.0', mapserverport)), app)
    except Exception as e:
        print(f"Failed to start server on port {mapserverport}. Error: {e}")
