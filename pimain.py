import io
import os
import time
import json
import socket
import config
import logging
import threading
import subprocess
from contextlib import redirect_stdout

def log(msg, level=logging.INFO, conn=None):
    """
    Log a message to the log file and print it to the console
    """
    if conn is not None:
        conn.sendall(json.dumps({"type": "log", "data": msg, "level": "log"}).encode("utf-8"))
        return
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
conn, addr = _socket.accept()
conn.settimeout(2)
log(f"Connection from {addr[0]}:{addr[1]}")
conn.sendall(json.dumps({"type": "log", "data": "Hello World from the AstroPi!", "level": "info"}).encode("utf-8"))
conn.sendall(json.dumps({"type": "connection", "data": "connected"}).encode("utf-8"))
filetransfer = FileTransferThread()
threading.Thread(target=filetransfer.start).start()

while True:
    # Receive data and decode it
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            data = conn.recv(1024).decode("utf-8")
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
        for d in data:
            command = d["command"]
            try:
                if command == "updateSystem":
                    print(subprocess.check_output(["sudo", "apt", "update", "-y", "&", "sudo", "apt", "upgrade", "-y"], stderr=subprocess.STDOUT))
                elif command == "pullUpdates":
                    print(subprocess.check_output(["git", "pull"], stderr=subprocess.STDOUT))
            except Exception as e:
                print(f"Error: {e}")
    if f.getvalue() != "":
        print
        conn.sendall(json.dumps({"type": "log", "data": f.getvalue(), "level": "log"}).encode("utf-8"))