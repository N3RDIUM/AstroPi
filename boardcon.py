import time
import json
import socket
import threading

class BoardCon:
    """
    BoardCon
    
    The BoardCon class is used to communicate with the Raspberry Pi board.
    """
    def __init__(self, ip, parent):
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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, 2077))
        self.fileTransferSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fileTransferSocket.connect((self.ip, 2078))
        threading.Thread(target=self.handle, args=(self.socket)).start()
        threading.Thread(target=self.handle_ft, args=(self.fileTransferSocket)).start()
        
    def handle(self, socket):
        while True:
            # Receive data and decode it
            data = socket.recv(1024).decode("utf-8")
            strlen = 0
            strlenend = 0
            _data = []
            # Split the data into a list of JSON objects
            while True:
                try:
                    strlenend += 1
                    print(data[strlen:strlenend])
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
                print(d)
                
    def handle_ft(self, socket):
        buffer = ""
        while True:
            # Receive data and decode it
            data = socket.recv(16384).decode("utf-8")
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
        with open(f"{self.fileSavePath}/{self.files_written}.dng", "wb") as f:
            f.write(buffer.encode("utf-8"))
            self.files_written += 1
            
    def send_config(self, config):
        self.socket.send(json.dumps(config).encode('utf-8'))