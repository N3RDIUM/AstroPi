# imports
import threading
import requests
import flask
import os
import logging

# Import constants
import Pi.constants as constants

# Get device IP from ifconfig
device_ip = os.popen("ifconfig").read().split("inet ")[1].split(" ")[0]

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
        self.comms_url = f"http://{self.ip}:{constants.ASTROPI_PORT}/"
        self.window.log(f"Board comms URL: {self.comms_url}", logging.DEBUG)
        self.set_state(constants.DISCONNECTED)
        self.session_running = False
        self.params = { # default params
            'image_count': '1', 
            'interval': '0', 
            'exposure_numerator': '1', 
            'exposure_denominator': '1',
            'iso': -1, 
            'focus': -2, 
            'brightness': 100, 
            'contrast': 100, 
            'exposure_compensation': 0, 
            'sharpness': 0, 
            'awb_gain_mode': 0, 
            'drc_strength': 0, 
            'image_denoise': 0, 
            'exposure_mode': 0, 
            'flash_mode': 0, 
            'resolution': 0, 
            'metering_mode': 0, 
            'effect_params': '', 
            'color_effect_u': '255',
            'color_effect_v': '255',
            'zoom_x': '0.0', 
            'zoom_y': '0.0', 
            'zoom_w': '1.0', 
            'zoom_h': '1.0'
        }
        # Create a Flask app to listen for board status updates
        self.app = flask.Flask(__name__)
        
        @self.app.route("/", methods=["POST"])
        def update():
            self._update(flask.request.form)
            # Stringify the form data
            form_data = ""
            for key, value in flask.request.form.items():
                form_data += f"{key}: {value}\n"
            self.window.log(f"Board update:\n{form_data}", logging.DEBUG)
        
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
        
    def kill_server(self):
        """
        Kill the Flask server
        """
        self.server_thread.join()
        
    def connect(self):
        """
        Connect to the board
        """        
        # Start the Flask app in a new thread
        def start_server():
            self.app.run(port=constants.ASTROPI_CLIENT_PORT, debug=True, use_reloader=False)
        self.server_thread = threading.Thread(target=start_server, daemon=True)
        self.server_thread.start()
        
        self.set_state(constants.CONNECTING)
        res = requests.post(self.comms_url + "connect", data={"device_ip": device_ip})
        self.window.log(f"Board connect response: {res.status_code} {res.text}", logging.INFO)
        if res.status_code == 200:
            self.set_state(constants.CONNECTED)
        else:
            self.set_state(constants.DISCONNECTED)
            raise Exception("Board connection failed (Error: " + res.text + ")")

    def set(self, key, value):
        """
        Set a value on the board
        """
        self.params[key] = value
        print(self.params)
    
    def update_params(self):
        for key, value in self.params.items():
            self.set_param(key, value)
            
    def set_param(self, key, value):
        response = requests.post(self.comms_url + "config", data={"key": key, "value": value})
        self.window.log(f"Board set response: {response.status_code} {response.text}", logging.DEBUG)
        
    def system(self, type):
        """
        Perform system tasks on the Pi
        """
        if type == constants.SYSTEM_UPDATE:
            response = requests.post(self.comms_url + "system", data={"command": type})
            self.window.log(f"Board system response: {response.status_code} {response.text}", logging.DEBUG)
        elif type == constants.PULL_UPDATES:
            response = requests.post(self.comms_url + "system", data={"command": type})
            self.window.log(f"Board system response: {response.status_code} {response.text}", logging.DEBUG)
        else:
            raise Exception("Invalid system command")
        
    def eval_settings(self):
        print(self.params)
        return True