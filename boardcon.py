# imports
import threading
import logging
import socket
import json
import time
import base64
import os

# Import constants
import Pi.constants as constants

class AstroPiBoard:
    """
    AstroPiBoard class
    
    This is allows the AstroPi application 
    to communicate with the AstroPi board.
    """
    def __init__(self, board_ip, window):
        """
        Initialize the AstroPi board
        """
        self.window = window
        self.ip = board_ip
        self.window.log(f"Board IP: {self.ip}", logging.DEBUG)
        self.set_state(constants.DISCONNECTED)
        self._config = { 
            'image_count': 1,
            'interval': 0,
            
            'ExposureTime': 1000000,
        }
        self.progress = {
            "image_count": 0
        }
        
    def set_state(self, state):
        """
        Set the state of the board
        """
        self.state = state
        if state == constants.DISCONNECTED:
            self.window.BoardStatus.setText(constants.DISCONNECTED_TEXT)
        elif state == constants.CONNECTED:
            self.window.BoardStatus.setText(constants.CONNECTED_TEXT)
        elif state == constants.CONNECTING:
            self.window.BoardStatus.setText(constants.CONNECTING_TEXT)
        else:
            self.window.BoardStatus.setText(constants.UNKNOWN_TEXT)
            
    def connect(self):
        """
        Connect to the board
        """        
        self.thread = threading.Thread(target=self.start_socket_client)
        self.thread.start()
        
    def terminate(self):
        """
        Terminate the connection to the board
        """
        self.set_state(constants.DISCONNECTED)
        self.socket.close()
        self.thread.join()
        
    # Start the socket client in a new thread
    def start_socket_client(self):
        self.set_state(constants.CONNECTING)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, constants.ASTROPI_PORT))
        self.window.log("Socket created successfully!")
        self.socket.send(constants.JSON_SEPARATOR.encode("utf-8"))
        self.file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_socket.connect((self.ip, constants.ASTROPI_TRANSFER_PORT))
        self.file_socket.send(json.dumps({
            "command": "connect",
        }).encode("utf-8"))
        threading.Thread(target=self._handle_file_transfer).start()
        self.socket.send(constants.JSON_SEPARATOR.encode("utf-8"))
        self.socket.send(json.dumps({
            "command": "connect",
        }).encode("utf-8"))
        self.socket.send(constants.JSON_SEPARATOR.encode("utf-8"))
        self.update__config()
        self.window.log("Synced config with board")
        while True:
            _data = self.socket.recv(1024).decode("utf-8")
            if not _data: continue
            _data = _data.split(constants.JSON_SEPARATOR)
            for data in _data:
                if not data: continue
                else: 
                    try:
                        data = json.loads(data)
                    except json.decoder.JSONDecodeError:
                        self.window.log("Received invalid JSON: " + data, logging.ERROR)
                        continue
                self.window.log(str(data["data"]), data["type"])
                if data["data"] == "Connected to AstroPi successfully!":
                    self.set_state(constants.CONNECTED)
                if self.state == constants.DISCONNECTED:
                    break
                
    def _handle_file_transfer(self):
        """
        Handle file transfer
        """
        while True:
            _data = self.file_socket.recv(16384).decode("utf-8")
            if not _data: continue
            else:
                if _data == constants.FILE_SEPARATOR:
                    self.progress["image_count"] += 1
                    self.window.log(f"Received image {self.progress['image_count']}", logging.INFO)
                    # self.window.update_progress()
                else:
                    _data = base64.b64decode(_data)
                    with open(os.path.join(self.window.save_dir, f"image_{self.progress['image_count']}.jpg"), "ab") as f:
                        f.write(_data)

    def set(self, key, value):
        """
        Set a value on the board
        """
        self._config[key] = value
        if self.state == constants.CONNECTED:
            if key not in ["image_count", "interval"]:
                self.socket.send(json.dumps({
                    "command": "set",
                    "key": key,
                    "value": value
                }).encode("utf-8"))
        
    def update__config(self):
        """
        Update the _config on the board
        """
        self.socket.send(json.dumps({
            "command": "setall",
            "config": self._config
        }).encode("utf-8"))
            
    def set_param(self, key, value):
        """
        Set a parameter on the board
        """
        self.socket.send(json.dumps({
            "command": "set",
            "key": key,
            "value": value
        }).encode("utf-8"))
        
    def system(self, type):
        """
        Perform system tasks on the Pi
        """
        self.socket.send(json.dumps({
            "command": "system",
            "type": type,
        }).encode("utf-8"))
        
    def eval_settings(self):
        """
        Evaluate the settings on the board
        before starting a session
        """
        try:
            self._config['image_count'] = int(self._config['image_count'])
            self._config['interval'] = int(self._config['interval'])
            self._config['ExposureTime'] = int(self._config['ExposureTime'])
            return True
        except Exception as e:
            self.window.log(f"Error evaluating settings: {e}", logging.ERROR)
            return False
        
    def start_session(self):
        """
        Start the session on the board
        """
        if self.eval_settings():
            self.update__config()
            self.socket.send(json.dumps({
                "command": "start"
            }).encode("utf-8"))
            self.socket.send(constants.JSON_SEPARATOR.encode("utf-8"))
            self.file_socket.send(json.dumps({
                "command": "connect",
            }).encode("utf-8"))
        else:
            self.window.log("Session start failed", logging.ERROR)
            
    def removeConfig(self, key):
        """
        Remove a config from the board
        """
        self._config.pop(key)