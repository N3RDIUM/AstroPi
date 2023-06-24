import os
from PyQt5 import QtWidgets
import time
import json
import config
import socket
import threading
import base64
import imageio
import rawpy
import base64
import base64
import re

def decode_base64(data, altchars=b'+/'):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
    missing_padding = len(data) % 4
    if missing_padding:
        data += b'='* (4 - missing_padding)
    return base64.b64decode(data, altchars)

class BoardCon:
    """
    BoardCon
    
    The BoardCon class is used to communicate with the Raspberry Pi board.
    """
    def __init__(self, ip, parent):
        """
        Initialize the BoardCon class
        """
        self.ip = ip
        self.parent = parent
        self.camdetails = {}
        self.config = {
            'ImageCount': 1,
            'Interval': 0,
            'ExposureTime': 1000000,
            'AnalogueGain': 1.0,
            'ResolutionX': 4056,
            'ResolutionY': 3040,
        }
        self.fileSavePath = "./"
        self.files_written = 0
        self.std = False
        
        # Attempt to connect to the board
        try:
            self.parent.setBoardStatus("<font color=\"yellow\">CONNECTING...</font>")
            time.sleep(0.1)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(2)
            self.socket.connect((self.ip, config.PORT))
            self.handler = threading.Thread(target=self.handle, args=(self.socket,))
            self.handler.start()
            self.verified = False
            t = time.time()
            while not self.verified:
                if time.time() - t > 2:
                    raise TimeoutError("Connection timed out!")
            self.parent.log(f"Connection established with AstroPi Board at {self.ip}", "info")
            self.parent.alertPopup("AstroPi", f"Connection established with AstroPi Board at {self.ip}", "info")
            self.parent.enableConfigTabs()
            self.parent.unlockButtons()
            self.parent.setBoardStatus("<font color=\"green\">CONNECTED</font>")
        except Exception as e:
            self.parent.log("Error: " + str(e), "error")
            self.parent.setBoardStatus("<font color=\"orange\">CONENCTION FAILED</font>")
            time.sleep(1)
            self.parent.setBoardStatus("<font color=\"red\">DISCONNECTED</font>")
            self.parent.alertPopup("AstroPi", "Connection failed! Please check the IP address and try again.", "error")
            raise e
        
    def handle(self, _socket):
        """
        Handle the data received from the board
        """
        while True:
            # Receive data and decode it
            try:
                data = _socket.recv(1024).decode("utf-8")
            except TimeoutError:
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
            # Handle the data
            for d in data:
                if d["type"] == "log":
                    self.parent.log(str(d["data"]), d["level"])
                elif d["type"] == "connection":
                    self.verified = True
                    self.fileTransferSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.fileTransferSocket.connect((self.ip, config.FILE_TRANSFER_PORT))
                    self.fileTransferHandler = threading.Thread(target=self.handle_ft)
                    self.fileTransferHandler.start()
                elif d["type"] == "camdetails":
                    self.camdetails = d["data"]
                    
    def handle_ft(self):
        """
        Handle the file transfer data received from the board
        """
        while True:
            _data = self.fileTransferSocket.recv(16384).decode("utf-8")
            if not _data: continue
            else:
                if _data == "|E|O|F|":
                    self.files_written += 1
                    self.parent.log(f"Received image {self.files_written}/{self.config['ImageCount']}", "info")
                else:
                    try:
                        _data = decode_base64(_data)
                        with open(os.path.join(self.fileSavePath, f"image{self.files_written}.dng"), "wb") as f:
                            f.write(_data)
                    except Exception as e:
                        self.window.log(f"Received invalid base64 data: {e}", "error")
                        continue
        
    def handle_ft_complete(self):
        with rawpy.imread(os.path.join(self.fileSavePath, f"image{self.files_written}.dng")) as raw:
            rgb = raw.postprocess()
        imageio.imsave(f"{self.fileSavePath}/temp.png", rgb)
        self.parent.Preview.currentWidget().setStyleSheet(f"""background-image: url(\"{self.fileSavePath}/temp.png);
                                    background-repeat: no-repeat; 
                                    background-position: center; 
                                    background-color: black;""")

    def send_config(self, config):
        """
        Send the configuration to the board
        """
        self.socket.send(json.dumps({"command": "setConfig", "config": config}).encode('utf-8'))
                
    def updateSystem(self):
        self.socket.send(json.dumps({"command": "updateSystem"}).encode('utf-8'))
        
    def pullUpdates(self):
        self.socket.send(json.dumps({"command": "pullUpdates"}).encode('utf-8'))
        
    def connectViaSSH(self):
        uname = self.parent.retrieveSSHUsername()
        # Start the SSH connection in a new terminal window
        if os.name == "nt":
            os.system(f"start cmd /k \"ssh {uname}@{self.ip}\"")
        else:
            self.parent.log("SSH connection started in a new terminal window.\nPlease make sure you have GNOME Terminal installed.", "green")
            os.system(f"gnome-terminal -- ssh {uname}@{self.ip}")
    
    def abortSession(self):
        self.socket.send(json.dumps({"command": "abortSession"}).encode('utf-8'))
        
    def startImaging(self):
        self.socket.send(json.dumps({"command": "startImaging"}).encode('utf-8'))
        
    def updateSettings(self):
        try:
            self.config = {
                'ImageCount': int(self.parent.ImageCount.text()),
                'Interval': int(self.parent.Interval.text()),
                'ExposureTime': int(self.parent.ExposureTime.text()),
                'AnalogueGain': self.config["AnalogueGain"] / 100,
                'ResolutionX': int(self.parent.ResolutionX.text()),
                'ResolutionY': int(self.parent.ResolutionY.text())
            }
            self.socket.send(json.dumps({
                "command": "updateSettings",
                "settings": self.config
            }).encode('utf-8'))
        except Exception as e:
            self.parent.log("Error: " + str(e), "error")
            self.parent.alertPopup("AstroPi", "Error validating settings: " + str(e), "error")
            
        _config = self.config
        self.parent.SettingsReview.setRowCount(len(_config))
        self.parent.SettingsReview.setColumnCount(2)
        self.parent.SettingsReview.setHorizontalHeaderLabels(["Setting", "Value"])
        for n, key in enumerate(sorted(_config.keys())):
            _key = key.replace("_", " ").title()
            self.parent.SettingsReview.setItem(n, 0, QtWidgets.QTableWidgetItem(_key))
            self.parent.SettingsReview.setItem(n, 1, QtWidgets.QTableWidgetItem(str(_config[key])))