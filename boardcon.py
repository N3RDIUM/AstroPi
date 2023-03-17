# imports
import threading
import requests
import flask
import socket
import logging

# Import constants
import Pi.constants as constants

# Get device IP
hostname = socket.gethostname()
device_ip = socket.gethostbyname(hostname)

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
            
        # Start the Flask app in a new thread
        def start_server():
            self.app.run(port=constants.ASTROPI_CLIENT_PORT, debug=True, use_reloader=False)
        self.server_thread = threading.Thread(target=start_server)
        self.server_thread.start()
        
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
        func = flask.request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        self.server_thread.join()
        self.set_state(constants.DISCONNECTED)
        
    def connect(self):
        """
        Connect to the board
        """
        self.set_state(constants.CONNECTING)
        res = requests.get(self.comms_url)
        self.window.log(f"Board connect response: {res.status_code} {res.text}", logging.INFO)
        if res.status_code == 200:
            self.set_state(constants.CONNECTED)
        else:
            self.set_state(constants.DISCONNECTED)
