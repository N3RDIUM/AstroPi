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
        self._config = { # default _config
            "ExposureTime": 1000000
        }
        self.progress = {
            "image_count": 0,
        }
        
    def set_state(self, state):
        """
        Set the state of the board
        """
        self.state = state
        if state == constants.DISCONNECTED:
            self.window.label_3.setText(constants.DISCONNECTED_TEXT)
        elif state == constants.CONNECTED:
            self.window.label_3.setText(constants.CONNECTED_TEXT)
        elif state == constants.CONNECTING:
            self.window.label_3.setText(constants.CONNECTING_TEXT)
        else:
            self.window.label_3.setText(constants.UNKNOWN_TEXT)
            
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
        
    def save_image(self, path, b64):
        """
        Save the received image
        """
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
        
    # Start the socket client in a new thread
    def start_socket_client(self):
        self.set_state(constants.CONNECTING)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, constants.ASTROPI_PORT))
        self.socket.send(json.dumps({
            "command": "connect",
        }).encode("utf-8"))
        time.sleep(1)
        self.update__config()
        while True:
            _data = self.socket.recv(1024).decode("utf-8")
            if not _data: continue
            else:
                _data = json.loads(_data)
                if not _data["type"] == "b64":
                    self.window.log(str(_data["data"]), _data["type"])
                else:
                    self.save_image(os.path.join(self.window.save_dir, _data["path"]), _data["data"])
                    self.window.log(f"Saved image to {os.path.join(self.window.save_dir, _data['path'])}", logging.INFO)
                
                if _data["data"] == "Connected to AstroPi successfully!":
                    self.set_state(constants.CONNECTED)
                
            if self.state == constants.DISCONNECTED:
                break

    def set(self, key, value):
        """
        Set a value on the board
        """
        self._config[key] = value
    
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
            self._config['exposure'] = int(self._config['exposure'])
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
        else:
            self.window.log("Session start failed", logging.ERROR)