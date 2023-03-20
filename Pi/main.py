import os
import socket
import json
import constants
import logging
import time
import base64
import time
import threading
import sys

# If the log file already exists, delete it
if os.path.exists("PiLog.txt"):
    os.remove("PiLog.txt")
logging.basicConfig(filename="PiLog.txt", level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

def log(msg, level=logging.INFO):
    """
    Log a message to the log file and print it to the console
    """
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
        _socket.bind((device_ip, constants.ASTROPI_PORT))
        log("Socket bound successfully!")
        break
    except OSError:
        print("Socket already in use, retrying in 5 seconds...")
        time.sleep(5)
_socket.listen(1)
_config = {}

class TransferThread:
    """
    This transfers the files over the socket
    """
    def __init__(self, conn):
        self.conn = conn
        self.filequeue = []
        
    def add_file(self, path):
        self.filequeue.append(path)
        
    def start(self):
        self.thread = threading.Thread(target=self._start)
        self.thread.start()
        
    def _start(self):
        time.sleep(0.1)
        while True:
            if not self.filequeue:
                time.sleep(1/1000)
                continue
            path = self.filequeue.pop(0)
            log("Sending file: " + path)
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
            for i in range(0, len(data), 4096):
                self.conn.send(data[i:i+4096].encode("utf-8"))
            log("Sent file: " + path)
            time.sleep(0.1)
            self.conn.send(constants.FILE_SEPARATOR.encode("utf-8"))
            os.remove(path)
            
class StreamThread:
    """
    Stream the output to ASTROPI_PREVIEW_PORT
    """
    def __init__(self, picam2):
        self.picam2 = picam2
        self.video_config = picam2.create_video_configuration({"size": (1280, 720)})
        self.picam2.configure(self.video_config)
        self.encoder = H264Encoder(1000000)
        self.streaming = False
        self.thread = threading.Thread(target=self.start)
        self.thread.start()

    def start(self):
        self.streaming = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((device_ip, constants.ASTROPI_PREVIEW_PORT))
            sock.listen()

            self.picam2.encoder = self.encoder

            conn, addr = sock.accept()
            stream = conn.makefile("wb")
            picam2.encoder.output = FileOutput(stream)
            picam2.start_encoder()
            picam2.start()
            while self.streaming:
                time.sleep(1/10)
            picam2.stop()
            picam2.stop_encoder()
            conn.close()
            
    def terminate(self):
        self.streaming = False
        self.thread.join()

try:
    try:
        conn, addr = _socket.accept()
        log('Connected by: ' + str(addr))
        file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_socket.bind((device_ip, constants.ASTROPI_TRANSFER_PORT))
        file_socket.listen(1)
        log("Waiting for transfer connection...")
        while True:
            fileconn, fileaddr = file_socket.accept()
            _data = fileconn.recv(1024)
            if not _data: continue
            _data = json.loads(_data)
            if _data["command"] == "connect":
                log("Connected to transfer client successfully!")
                break
        transfer = TransferThread(fileconn)
        transfer.start()
        from picamera2 import Picamera2 
        from picamera2.encoders import H264Encoder
        from picamera2.outputs import FileOutput
        
        # Start streaming to constants.ASTROPI_PREVIEW_PORT
        picam2 = Picamera2()
        # stream = StreamThread(picam2)
        
        while True:
            data = conn.recv(1024)
            if not data: continue
            log("Received: " + str(data))
            def _log(msg, level=logging.INFO):
                conn.send(json.dumps({
                    "type": level,
                    "data": msg
                }).encode("utf-8"))
                print(f"Sent: {msg}")
                time.sleep(1/10)
            data = json.loads(data)
            if data["command"] == "connect":
                _log("Connected to AstroPi successfully!")
            elif data["command"] == "set":
                _config[data["key"]] = data["value"]
                _log("Set " + data["key"] + " to " + data["value"] + " successfully!")
            elif data["command"] == "setall":
                _config = data["config"]
                _log("Set all config values successfully!")
            elif data["command"] == "get":
                _log(f"Value of {data['key']}: {_config[data['key']]}")
            elif data["command"] == "system":
                if data["type"] == constants.PULL_UPDATES:
                    _log("Pulling updates... Please wait")
                    _log(os.popen("git pull").read(), logging.DEBUG)
                elif data["type"] == constants.SYSTEM_UPDATE:
                    _log("Updating system... Please wait")
                    _log(os.popen("sudo apt-get update").read(), logging.DEBUG)
                    _log(os.popen("sudo apt-get upgrade -y").read(), logging.DEBUG)
                else:
                    _log("Unknown system command: " + data["type"], logging.ERROR)
            elif data["command"] == "start":
                
                _log("Starting session...")
                # Remove values not advertised by libcamera
                image_count = _config.pop("image_count")
                interval = _config.pop("interval")
                # Also remove all "None" values
                for key in list(_config.keys()):
                    if _config[key] == "None":
                        _config.pop(key)
                time.sleep(1)
                
                _log("Configuring camera...")
                # Configure the camera
                print(picam2.camera_controls)
                # Since we are taking images of the sky, set focus to infinity
                _config["LensPosition"] = 0
                camera_config = picam2.create_still_configuration(
                    main={
                        "size": (1920, 1080),
                    },
                    controls=_config
                )
                picam2.configure(camera_config)
                
                # Start the session
                _log("Starting session...")
                picam2.start()
                time.sleep(2) # Warm up the camera
                
                # Go to captures directory
                for i in range(0, image_count):
                    _log("Capturing image " + str(i + 1) + " of " + str(image_count))
                    picam2.capture_file("capture_" + str(i) + ".jpg")
                    transfer.add_file("capture_" + str(i) + ".jpg")
                    if interval / 1000000 - 1/10 > 0:
                        time.sleep(interval / 1000000 - 1/10)
                    else:
                        continue
                _log("Session complete! Stopping camera...")
                picam2.stop()
                time.sleep(1)
                
                if len(transfer.filequeue) > 0:
                    _log("Waiting for transfer to complete...")
                    while True:
                        if len(transfer.filequeue) == 0:
                            break
                        time.sleep(1)
                _log("Transfer complete!")
                time.sleep(1)
                _log("Exiting...")
                conn.close()
    except KeyboardInterrupt:
        log("KeyboardInterrupt")
        _socket.close()
        sys.exit(0)
except Exception as e:
    if conn:
        conn.send(json.dumps({
            "type": logging.ERROR,
            "data": "Error: " + str(e)
        }).encode("utf-8"))
        conn.close()
    log("Error: " + str(e) + ". Killing server...")
    _socket.close()
    sys.exit(1)