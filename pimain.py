import os
import time
import json
import socket
import config
import base64
import logging
import threading
import subprocess
from picamera2 import *

def log(msg, level=logging.INFO, conn=None):
    """
    Log a message to the log file and print it to the console
    """
    if type(msg) is bytes:
        msg = msg.decode("utf-8")
    if conn is not None:
        conn.sendall(json.dumps({"type": "log", "data": msg, "level": level}).encode("utf-8"))
        return
    else:
        logging.log(level, msg)
    print(msg)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
device_ip = s.getsockname()[0]
s.close()
log("Device IP: " + device_ip)

_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
log("Socket created successfully!")
while True:
    try:
        _socket.bind((device_ip, config.PORT))
        log("Socket bound successfully!")
        break
    except OSError:
        print("Socket already in use, retrying in 5 seconds...")
        time.sleep(5)
_socket.listen(1)

class FileTransferThread:
    """
    This transfers the files over the socket
    """
    def __init__(self, client):
        self.client = client
        self.filequeue = []
        self.filesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log("File transfer socket created successfully!")
        while True:
            try:
                self.filesocket.bind((device_ip, config.FILE_TRANSFER_PORT))
                log("File transfer socket bound successfully!")
                break
            except OSError:
                print("File transfer socket already in use, retrying in 5 seconds...")
                time.sleep(5)
        self.filesocket.listen(1)
        
    def add_file(self, path):
        self.filequeue.append(path)
        
    def start(self):
        conn, addr = self.filesocket.accept()
        self.connection = (conn, addr)
        self.conn = conn
        self.thread = threading.Thread(target=self._start)
        self.thread.start()
        
    def _start(self):
        time.sleep(5)
        while True:
            if not self.filequeue:
                time.sleep(1/1000)
                continue
            path = self.filequeue.pop(0)
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
            log("[IMAGE_TRANSFER ASTROPI] Sending file: " + path, "debug", self.conn)
            for i in range(0, len(data), 4096):
                self.conn.send(data[i:i+4096].encode("utf-8"))
            time.sleep(0.1)
            self.conn.send("|||".encode("utf-8"))
            os.remove(path)

log("Listening for connections...")
conn, addr = _socket.accept()
conn.settimeout(2)
log(f"Connection from {addr[0]}:{addr[1]}")
conn.sendall(json.dumps({"type": "log", "data": "Hello World from the AstroPi!", "level": "info"}).encode("utf-8"))
conn.sendall(json.dumps({"type": "connection", "data": "connected"}).encode("utf-8"))
if not os.path.exists("images"):
    os.mkdir("images")
filetransfer = FileTransferThread(client=conn)
filetransfer.start()
settings = {}
abort=False

while True:
    # Receive data and decode it
    try:
        data = conn.recv(1024).decode("utf-8")
    except socket.timeout:
        continue
    strlen = 0
    strlenend = 0
    _data = []
    # Split the data into a list of JSON objects
    while True:
        try:
            strlenend += 1
            _data.append(json.loads(data[strlen:strlenend]))
            strlen = strlenend
            strlenend = strlenend + 1
        except json.decoder.JSONDecodeError:
            continue
        finally:
            if strlenend > len(data):
                break
    data = _data
    for d in data:
        command = d["command"]
        try:
            if command == "updateSystem":
                log(subprocess.check_output(["sudo", "apt", "update", "-y", "&", "sudo", "apt", "upgrade", "-y"], stderr=subprocess.STDOUT), conn=conn)
            elif command == "pullUpdates":
                log(subprocess.check_output(["git", "pull"], stderr=subprocess.STDOUT), conn=conn)
            elif command == "updateSettings":
                settings = d["settings"]
                print("New config:")
                for key in settings:
                    print(f"\t{key}: {settings[key]}")
            elif command == "startImaging":
                log("Starting imaging...", "success", conn=conn)
                camera = Picamera2()
                camera_config = camera.configure(camera_config=camera.create_still_configuration(
                    main={}, raw={}
                ))
                with camera.controls as ctrl:
                    ctrl.AnalogueGain = settings["AnalogueGain"]
                    ctrl.ExposureTime = settings["ExposureTime"]
                log(f"Config success!\nCamera config: {camera_config}", conn=conn)
                # Warm up the camera
                camera.start()
                time.sleep(2)
                log("Camera warmed up! Starting imaging session...", conn=conn)
                # Start the imaging session
                for imageID in range(settings["ImageCount"]):
                    time.sleep(settings["Interval"]/1000000)
                    log(f"[ASTROPI_SESSION] Capturing image {imageID+1} of {settings['ImageCount']}", conn=conn)
                    camera.capture_file(f"images/{imageID}.dng", name="raw")
                    filetransfer.add_file(f"images/{imageID}.dng")
                    if abort: 
                        abort=False
                        break # TODO: Add abort thread
            elif command == "abortSession":
                log("<p color=\"yellow\">Aborting session...</p>", "warning", conn=conn)
        except Exception as e:
            log(f"Error: {e}", level="error", conn=conn)