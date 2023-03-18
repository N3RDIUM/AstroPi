import os
import socket
import json
import constants
import logging
import time
import sys

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
_socket.bind((device_ip, constants.ASTROPI_PORT))
_socket.listen(1)

_config = { # default _config
    'session_time': 2, # SESSION SETTINGS
    'processor_fan_state': 0,
    'processor_fan_speed': 0,
    'camera_fan_state': 0,
    'camera_fan_speed': 0,
    'transfer_quality': 0,        
    'image_count': '1', # CAMERA SETTINGS
    'interval': '0', 
    'exposure': '1', 
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
try:
    conn, addr = _socket.accept()
    log('Connected by: ' + str(addr))
    while True:
        try:
            data = conn.recv(1024)
            if not data: continue
            log("Received: " + str(data))
            data = json.loads(data)
            if data["command"] == "connect":
                conn.send(json.dumps({
                    "status": "connected",
                    "response": "success",
                    "data": "Connected to the AstroPi successfully!"
                }).encode("utf-8"))
            elif data["command"] == "set":
                _config[data["key"]] = data["value"]
                conn.send(json.dumps({
                    "status": "connected",
                    "response": "success",
                    "data": "Set " + data["key"] + " to " + str(data["value"])
                }).encode("utf-8"))
            elif data["command"] == "setall":
                _config = data["config"]
                conn.send(json.dumps({
                    "status": "connected",
                    "response": "success",
                    "data": "Set all config values successfully!" 
                }).encode("utf-8"))
            elif data["command"] == "get":
                conn.send(json.dumps({
                    "status": "connected",
                    "response": "success",
                    "data": _config[data["key"]]
                }).encode("utf-8"))
            elif data["command"] == "system":
                if data["type"] == constants.PULL_UPDATES:
                    conn.send(json.dumps({
                        "status": "connected",
                        "response": "success",
                        "data": os.popen("git pull").read()
                    }).encode("utf-8"))
                elif data["type"] == constants.SYSTEM_UPDATE:
                    conn.send(json.dumps({
                        "status": "connected",
                        "response": "success",
                        "data": os.popen("sudo apt-get update && sudo apt-get upgrade -y").read()
                    }).encode("utf-8"))
                else:
                    conn.send(json.dumps({
                        "status": "connected",
                        "response": "Error: Invalid system command",
                        "data": "Invalid system command"
                    }).encode("utf-8"))
            elif data["command"] == "start":
                conn.send(json.dumps({
                    "status": "connected",
                    "response": "init",
                    "data": "Initializing camera..."
                }).encode("utf-8"))
                import picamera
                camera = picamera.PiCamera()
                
                # Configure the camera
                if _config["iso"] == constants.AUTO:
                    _config["iso"] = "auto"
                camera.iso = _config["iso"]

                if _config["focus"] == constants.AUTO:
                    _config["focus"] = "auto"
                elif _config["focus"] == constants.INFINITY:
                    _config["focus"] = "infinity"
                camera.exposure_mode = _config["focus"]

                if _config["image_denoise"] == 0:
                    camera.image_denoise = False
                else:
                    camera.image_denoise = True

                camera.brightness = _config["brightness"]
                camera.contrast = _config["contrast"]
                camera.exposure_compensation = _config["exposure_compensation"]
                camera.sharpness = _config["sharpness"]
                camera.shutter_speed = _config["exposure"]
                camera.resolution = (_config["resolution_x"], _config["resolution_y"])

                awb_modes = camera.AWB_MODES
                camera.awb_mode = awb_modes[_config["awb_mode"]]
                exposure_modes = camera.EXPOSURE_MODES
                camera.exposure_mode = exposure_modes[_config["exposure_mode"]]
                flash_modes = camera.FLASH_MODES
                camera.flash_mode = flash_modes[_config["flash_mode"]]
                metering_modes = camera.METER_MODES
                camera.meter_mode = metering_modes[_config["metering_mode"]]
                drc_strengths = camera.DRC_STRENGTHS
                camera.drc_strength = drc_strengths[_config["drc_strength"]]

                camera.zoom = (_config["zoom_x"], _config["zoom_y"], _config["zoom_w"], _config["zoom_h"])
                camera.color_effects = (_config["color_effect_u"], _config["color_effect_v"])
                
                conn.send(json.dumps({
                    "status": "connected",
                    "response": "init",
                    "data": "Warming up..."
                }).encode("utf-8"))
                camera.start()
                time.sleep(2)
                capture_config = camera.create_still_configuration(raw={})
                for i in range(int(_config["image_count"])):
                    conn.send(json.dumps({
                        "status": "connected",
                        "response": "session",
                        "data": f"Capturing image {i+1} of {int(_config['image_count'])}..."
                    }).encode("utf-8"))
                    buffers, metadata = camera.switch_mode_and_capture_buffers(capture_config, ["main", "raw"])
                    camera.helpers.save(camera.helpers.make_image(buffers[0], capture_config["main"]), metadata, "full.jpg")
                    camera.helpers.save_dng(buffers[1], metadata, capture_config["raw"], "full.dng")
                    camera.release()
                camera.close()
                conn.send(json.dumps({
                    "status": "connected",
                    "response": "session",
                    "data": "Done!"
                }).encode("utf-8"))
        except Exception as e:
            log("Error: " + str(e), logging.ERROR)
except KeyboardInterrupt:
    log("KeyboardInterrupt")
    _socket.close()
    sys.exit(0)