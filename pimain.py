import time
import json
import socket
import config
import logging
import threading

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
        _socket.bind((device_ip, config.PORT))
        log("Socket bound successfully!")
        break
    except OSError:
        print("Socket already in use, retrying in 5 seconds...")
        time.sleep(5)
_socket.listen(1)

class FileTransferThread:
    filesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __init__(self):
        log("File transfer socket created successfully!")
        while True:
            try:
                self.filesocket.bind((device_ip, config.FILE_TRANSFER_PORT))
                log("File transfer socket bound successfully!")
                break
            except OSError:
                print("File transfer socket already in use, retrying in 5 seconds...")
                time.sleep(5)
        self.filesocket.listen(1)
    
    def start(self):
        conn, addr = self.filesocket.accept()
        self.connection = (conn, addr)

log("Listening for connections...")
while True:
    conn, addr = _socket.accept()
    conn.settimeout(2)
    log(f"Connection from {addr[0]}:{addr[1]}")
    conn.sendall(json.dumps({"type": "log", "data": "Hello World from the AstroPi!", "level": "info"}).encode("utf-8"))
    conn.sendall(json.dumps({"type": "connection", "data": "connected"}).encode("utf-8"))
    filetransfer = FileTransferThread()
    threading.Thread(target=filetransfer.start).start()