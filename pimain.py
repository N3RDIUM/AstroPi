import os
import time
import json
import socket
import config
import logging
from struct import pack
import subprocess
DEV = False
if not DEV:
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
        conn, addr = self.filesocket.accept()
        self.connection = (conn, addr)
        self.conn = conn
        
    def add_file(self, path):
        self.filequeue.append(path)
    
    def send(self, filename):
        t = time.time()
        with open(filename, "rb") as f:
            data = f.read()
        length = pack('>Q', len(data))
        self.conn.send(length)
        self.conn.send(data)
        log(f"Sent file in {time.time()-t} seconds", "debug", self.client)

log("Listening for connections...")
conn, addr = _socket.accept()
conn.settimeout(2)
log(f"Connection from {addr[0]}:{addr[1]}")
print("\n")
conn.sendall(json.dumps({"type": "log", "data": "Hello World from the AstroPi!", "level": "info"}).encode("utf-8"))
conn.sendall(json.dumps({"type": "connection", "data": "connected"}).encode("utf-8"))
if not os.path.exists("images"):
    os.mkdir("images")
filetransfer = FileTransferThread(client=conn)
settings = {}
abort=False
camera = None
imageID = 0
if not DEV:
    camera = Picamera2()
    conn.sendall(json.dumps({
        "type": "camdetails", 
        "data": list(camera.global_camera_info())
    }).encode("utf-8"))
    log(f"Warming up camera...", conn=conn)
    camera.start()
    time.sleep(2)
    log("Camera warmed up successfully!", conn=conn)

def handleCommand(data, camera):
    global imageID
    global settings
    global abort
    for d in data:
        command = d["command"]
        try:
            if command == "updateSystem":
                log(subprocess.check_output(["sudo", "apt", "update", "-y", "&", "sudo", "apt", "upgrade", "-y"], stderr=subprocess.STDOUT), conn=conn)
            elif command == "pullUpdates":
                log(subprocess.check_output(["git", "pull"], stderr=subprocess.STDOUT), conn=conn)
            elif command == "updateSettings":
                settings = d["settings"]
                if camera:
                    with camera.controls as ctrl:
                        ctrl.ExposureTime = settings["ExposureTime"]
                        ctrl.AnalogueGain = settings["AnalogueGain"]
            elif command == "shutter":
                log(f"[ASTROPI_SESSION] Capturing image {imageID}", "success", conn=conn)
                conn.sendall(json.dumps({"type": "camstatus", "data": {"capturing": True, "abort": False}}).encode("utf-8"))
                if camera:
                    time.sleep(settings["Interval"]/1000000)
                    camera.capture_file(f"images/{imageID}.dng", name="raw")
                    filetransfer.send(f"images/{imageID}.dng")
                    log(f"[ASTROPI_SESSION] Captured image {imageID}", conn=conn)
                imageID += 1
                conn.sendall(json.dumps({"type": "camstatus", "data": {"capturing": False, "abort": False}}).encode("utf-8"))
            elif command == "abortSession":
                log("<p color=\"yellow\">[ASTROPI_SESSION] Aborting session after next capture...</p>", "warning", conn=conn)
                conn.sendall(json.dumps({"type": "camstatus", "data": {"capturing": False, "abort": True}}).encode("utf-8"))
        except Exception as e:
            log(f"Error: {e}", level="error", conn=conn)

while True:
    # Receive data and decode it
    try:
        conn.settimeout(2)
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
    handleCommand(data, camera)