import os
from PyQt5 import QtWidgets
import time
import json
import config
import socket
import threading
import imageio
import rawpy
from struct import unpack
        
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
        self.camstatus = {
            "capturing": False,
            "abort": False,
        }
        self.config = {
            'Frames': 1,
            'Interval': 0,
            'ExposureTime': 1000000,
            'AnalogueGain': 1.28,
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
            self.parent.enableConfigTab()
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
                try:
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
                    elif d["type"] == "camstatus":
                        self.camstatus.update(d["data"])
                except Exception as e:
                    self.parent.log(f"Exception in receive thread: {e}", "error")
                    
    def handle_ft(self):
        """
        Handle file transfer
        """
        while True:
            try:
                bs = self.fileTransferSocket.recv(8)
                (length,) = unpack('>Q', bs)
                data = b''
                while len(data) < length:
                    to_read = length - len(data)
                    dat = self.fileTransferSocket.recv(
                        4096 if to_read > 4096 else to_read)
                    data += dat
                    path = os.path.join(self.fileSavePath, f"image_{self.files_written}.dng")
                    if not self.std:
                        os.path.join(self.fileSavePath, f"temp.dng")
                    with open(path, "ab") as f:
                        f.write(dat)
                self.handle_ft_complete()
                self.files_written += 1
            except Exception as e:
                pass
        
    def handle_ft_complete(self):
        try:
            path = os.path.join(self.fileSavePath, f"image_{self.files_written}.dng")
            if not self.std:
                os.path.join(self.fileSavePath, f"temp.dng")
            with rawpy.imread(path) as raw:
                rgb = raw.postprocess()
            # Downscale the image 2x for speed
            # TODO: Make this a setting
            rgb = rgb[::2, ::2]
            imageio.imsave(f"{self.fileSavePath}/temp.png", rgb)
            self.parent.preview(f"{self.fileSavePath}/temp.png")
        except Exception as e:
            self.parent.log("Error updating preview: " + str(e), "error")

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
        
    def shutter(self):
        threading.Thread(target=self._shutter).start()
        
    def _shutter(self):
        for i in range(self.config["Frames"]):
            if self.camstatus["abort"]: break
            self.socket.send(json.dumps({"command": "shutter"}).encode('utf-8'))
            self.camstatus["capturing"] = True
            while self.camstatus["capturing"]: pass
        
    def updateSettings(self):
        try:
            self.config = {
                'Frames': int(self.parent.Frames.text()),
                'Interval': int(self.parent.Interval.text()),
                'ExposureTime': int(self.parent.ExposureTime.text()),
                'AnalogueGain': float(self.parent.ISO.value() * 16) / 100,
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