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
            'session_time': 2, # SESSION SETTINGS
            'processor_fan_state': 0,
            'processor_fan_speed': 0,
            'camera_fan_state': 0,
            'camera_fan_speed': 0,
            'transfer_quality': 0,        
            'image_count': '1', # CAMERA SETTINGS
            'interval': '0', 
            'exposure': '100000', 
            'iso': -1, 
            'focus': -2, 
            'brightness': 50, 
            'contrast': 100, 
            'exposure_compensation': 0, 
            'sharpness': 0, 
            'awb_mode': 0, 
            'drc_strength': 0, 
            'image_denoise': 0, 
            'exposure_mode': 0, 
            'flash_mode': 0, 
            'metering_mode': 0, 
            'effect__config': '', 
            'color_effect_u': '255',
            'color_effect_v': '255',
            'zoom_x': '0.0', 
            'zoom_y': '0.0', 
            'zoom_w': '1.0', 
            'zoom_h': '1.0',
            'resolution_x': '4608', # IMAGE RESOLUTIONS
            'resolution_y': '2592',
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
            data = [self.socket.recv(1024).decode("utf-8")]
            if not data: continue
            else:
                decode_complete = False
                while not decode_complete:
                    for _data in data:
                        try:
                            data[data.index(_data)] = json.loads(_data)
                            decode_complete = True
                        except json.decoder.JSONDecodeError as e:
                            error_char = e.doc[e.pos]
                            data[data.index(_data)] = _data.split(error_char)[0]
                            _data = _data.split(error_char)[1]
                            data.append(_data)
                for _data in data:
                    if not _data["type"] == "b64":
                        self.window.log(str(_data["data"]), _data["type"])
                    else:
                        self.save_image(os.path.join(self.window.save_dir, _data["path"]), _data["data"])
                    
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
            self._config['session_time'] = int(self._config['session_time'])
            self._config['processor_fan_state'] = int(self._config['processor_fan_state'])
            self._config['processor_fan_speed'] = int(self._config['processor_fan_speed'])
            self._config['camera_fan_state'] = int(self._config['camera_fan_state'])
            self._config['camera_fan_speed'] = int(self._config['camera_fan_speed'])
            self._config['transfer_quality'] = int(self._config['transfer_quality'])
            
            self._config['image_count'] = int(self._config['image_count'])
            self._config['interval'] = int(self._config['interval'])
            self._config['exposure'] = int(self._config['exposure'])
            self._config['iso'] = int(self._config['iso'])
            self._config['focus'] = int(self._config['focus'])
            self._config['brightness'] = int(self._config['brightness'])
            self._config['contrast'] = int(self._config['contrast'])
            self._config['exposure_compensation'] = int(self._config['exposure_compensation'])
            self._config['sharpness'] = int(self._config['sharpness'])
            self._config['awb_mode'] = int(self._config['awb_mode'])
            self._config['drc_strength'] = int(self._config['drc_strength'])
            self._config['image_denoise'] = int(self._config['image_denoise'])
            self._config['exposure_mode'] = int(self._config['exposure_mode'])
            self._config['flash_mode'] = int(self._config['flash_mode'])
            self._config['metering_mode'] = int(self._config['metering_mode'])
            self._config['color_effect_u'] = int(self._config['color_effect_u'])
            self._config['color_effect_v'] = int(self._config['color_effect_v'])
            self._config['zoom_x'] = float(self._config['zoom_x'])
            self._config['zoom_y'] = float(self._config['zoom_y'])
            self._config['zoom_w'] = float(self._config['zoom_w'])
            self._config['zoom_h'] = float(self._config['zoom_h'])
            
            self._config['resolution_x'] = int(self._config['resolution_x'])
            self._config['resolution_y'] = int(self._config['resolution_y'])
            
            # self._config["effect__config"] = json.loads(self._config["effect__config"])
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