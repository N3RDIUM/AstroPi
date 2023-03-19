import os
import socket
import json
import constants
import logging
import time
import sys
import time
import threading
from transferrer import Transferrer

# If the log file already exists, delete it
if os.path.exists("PiLog.txt"):
    os.remove("PiLog.txt")
logging.basicConfig(filename="PiLog.txt", level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

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
        _socket.bind((device_ip, constants.ASTROPI_PORT))
        log("Socket bound successfully!")
        break
    except OSError:
        print("Socket already in use, retrying in 5 seconds...")
        time.sleep(5)
_socket.listen(1)

# Now you'll ask me why I'm doing this.
# Well, it makes it easier to look at the max min and default values of the config
_config = { 
#   'Example': (min, max, default)[2], #=setting, ##=not added to UI yet
    'AwbMode': (0, 7, 0)[2], 
    'Sharpness': (0.0, 16.0, 1.0)[2], 
    'NoiseReductionMode': (0, 4, 0)[2], #
    'FrameDurationLimits': (33333, 120000, None)[2], ##
    'Contrast': (0.0, 32.0, 1.0)[2], 
    'ColourCorrectionMatrix': (-16.0, 16.0, None)[2], 
    'ExposureValue': (-8.0, 8.0, 0.0)[2], 
    'AeExposureMode': (0, 3, 0)[2], #
    'Saturation': (0.0, 32.0, 1.0)[2], 
    'ColourGains': (0.0, 32.0, None)[2], 
    'AfMode': (0, 2, 0)[2], #
    'LensPosition': (0.0, 32.0, 1.0)[2], 
    'AfMetering': (0, 1, 0)[2], #
    'Brightness': (-1.0, 1.0, 0.0)[2], 
    'AfSpeed': (0, 1, 0)[2], #
    'AeMeteringMode': (0, 3, 0)[2], #
    'AwbEnable': (False, True, None)[2], #
    'AfWindows': ((0, 0, 0, 0), (65535, 65535, 65535, 65535), (0, 0, 0, 0))[2], ##
    'AfPause': (0, 2, 0)[2], #
    'AeConstraintMode': (0, 3, 0)[2], #
    'AeEnable': (False, True, None)[2], #
    'AnalogueGain': (1.0, 16.0, None)[2], 
    'AfRange': (0, 2, 0)[2], #
    'ExposureTime': (0, 66666, None)[2], 
    'ScalerCrop': ((0, 0, 0, 0), (65535, 65535, 65535, 65535), (0, 0, 0, 0))[2], ##
    'AfTrigger': (0, 1, 0)[2] #
}

try:
    try:
        conn, addr = _socket.accept()
        log('Connected by: ' + str(addr))
        while True:
            data = conn.recv(1024)
            if not data: continue
            log("Received: " + str(data))
            def _log(msg, level=logging.INFO):
                conn.send(json.dumps({
                    "type": level,
                    "data": msg
                }).encode("utf-8"))
                print(f"Sent: {msg}")
                time.sleep(1/10)
            data = json.loads(data)
            if data["command"] == "connect":
                _log("Connected to AstroPi successfully!")
            elif data["command"] == "set":
                _config[data["key"]] = data["value"]
                _log("Set " + data["key"] + " to " + data["value"] + " successfully!")
            elif data["command"] == "setall":
                _config = data["config"]
                _log("Set all config values successfully!")
            elif data["command"] == "get":
                _log(f"Value of {data['key']}: {_config[data['key']]}")
            elif data["command"] == "system":
                if data["type"] == constants.PULL_UPDATES:
                    _log("Pulling updates... Please wait")
                    _log(os.popen("git pull").read(), logging.DEBUG)
                elif data["type"] == constants.SYSTEM_UPDATE:
                    _log("Updating system... Please wait")
                    _log(os.popen("sudo apt-get update").read(), logging.DEBUG)
                    _log(os.popen("sudo apt-get upgrade -y").read(), logging.DEBUG)
                else:
                    _log("Unknown system command: " + data["type"], logging.ERROR)
            elif data["command"] == "start":
                _log("Starting session...")
                transferrer = Transferrer(conn) # TODO: _config["transfer_quality"]
                thread = threading.Thread(target=transferrer.start)
                thread.start()
                time.sleep(1)
                
                _log("Configuring camera...")
                # We import this here because this pkg is only available on the Pi
                # and we don't want to import it on the PC while testing
                from picamera2 import Picamera2 
                
                # Configure the camera
                picam2 = Picamera2()
                print(picam2.camera_controls)
                camera_config = picam2.create_still_configuration(
                    main={
                        "size": (1920, 1080),
                    },
                    controls=_config
                )
                picam2.configure(camera_config)
                
                # Start the session
                _log("Starting session...")
                picam2.start()
                time.sleep(2) # Warm up the camera
                
                # Go to captures directory
                for i in range(0, _config["image_count"]):
                    _log("Capturing image " + str(i + 1) + " of " + str(_config["image_count"]))
                    picam2.capture_file("capture_" + str(i) + ".jpg")
                    if _config["interval"] / 1000000 - 1/10 > 0:
                        time.sleep(_config["interval"] / 1000000 - 1/10)
                    else:
                        continue
                _log("Session complete! Stopping camera and transfer thread...")
                picam2.stop()
                transferrer.stop()
    except KeyboardInterrupt:
        log("KeyboardInterrupt")
        _socket.close()
        sys.exit(0)
except Exception as e:
    if conn:
        conn.send(json.dumps({
            "type": logging.ERROR,
            "data": "Error: " + str(e)
        }).encode("utf-8"))
        conn.close()
    log("Error: " + str(e) + ". Killing server...")
    _socket.close()
    sys.exit(1)