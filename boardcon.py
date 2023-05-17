import time
import json
import config
import socket
import threading

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
        self.config = {
            'ImageCount': 1,
            'Interval': 0,
            'ExposureTime': 1000000,
            'ISO': 100,
            'ResolutionX': 4056,
            'ResolutionY': 3040,
        }
        self.fileSavePath = "./"
        self.files_written = 0
        
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
                    self.parent.log(d["data"], d["level"])
                elif d["type"] == "connection":
                    self.verified = True
                    self.fileTransferSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.fileTransferSocket.connect((self.ip, config.FILE_TRANSFER_PORT))
                    self.fileTransferHandler = threading.Thread(target=self.handle_ft)
                    self.fileTransferHandler.start()
                    
    def handle_ft(self):
        """
        Handle the file transfer data received from the board
        """
        _socket = self.fileTransferSocket
        buffer = ""
        while True:
            # Receive data and decode it
            data = _socket.recv(16384).decode("utf-8")
            if not data: continue # If there is no data, continue
            else: # If there is data, handle it
                # Split the data according to the delimiter
                data = data.split("|||")
                if len(data) == 2: # If there are two elements in the list, then the delimiter was found
                    buffer += data[0]
                    self.handle_buffer(buffer) # Clear the buffer, i.e. write the data to a file
                    buffer = ""
                    buffer += data[1]
                else: # If there is only one element in the list, then the delimiter was not found
                    buffer = data[0]
    
    def handle_buffer(self, buffer):
        """
        Save the contents of a buffer to a file
        """
        with open(f"{self.fileSavePath}/{self.files_written}.dng", "wb") as f:
            f.write(buffer.encode("utf-8"))
            self.files_written += 1
            
    def send_config(self, config):
        """
        Send the configuration to the board
        """
        self.socket.send(json.dumps(config).encode('utf-8'))