import flask
import requests
import picamera
import threading
import os
import logging
import constants

# If the log file already exists, delete it
if os.path.exists("PiLog.txt"):
    os.remove("PiLog.txt")
logging.basicConfig(filename="PiLog.txt", level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

def log(msg, level=logging.INFO):
    """
    Log a message to the log file and print it to the console
    """
    logging.log(level, msg)

# Get the ifconfig ip address
ip = os.popen("ifconfig").read().split("inet ")[1].split(" ")[0]
log(f"Device IP: {ip}")
log(f"Device port: {constants.ASTROPI_PORT}")

# Create the Flask app
app = flask.Flask(__name__)

# Config variables
params = {}

@app.route("/connect", methods=["POST"])
def communicate():
    """
    Communicate with the AstroPi board
    """
    # Get the data from the request
    data = flask.request.form
    global client_ip
    client_ip = data["device_ip"]
    return flask.jsonify({"success": True})

@app.route("/config", methods=["POST"])
def config():
    """
    Set a configuration value
    """
    # Get the data from the request
    data = flask.request.form
    key = data["key"]
    value = data["value"]
    params[key] = value
    
    return flask.jsonify({
        "success": True,
        "message": f"Set {key} to {value}",
    })

@app.route("/getconfig", methods=["GET"])
def getconfig():
    """
    Get a configuration value
    """
    # Get the data from the request
    return flask.jsonify({
        "success": True,
        "message": params,
    })
    
@app.route("/system", methods=["POST"])
def system():
    """
    System maintainance tasks
    """
    # Get the data from the request
    data = flask.request.form
    command = data["command"]
    if command == constants.PULL_UPDATES:
        # Pull updates from the GitHub repo
        os.system("cd .. && git pull")
        os.system("cd Pi")
        return flask.jsonify({
            "success": True,
            "message": "Pulled updates from GitHub"
        })
    elif command == constants.SYSTEM_UPDATE:
        # Update the system
        os.system("sudo apt update && sudo apt upgrade -y")
        return flask.jsonify({
            "success": True,
            "message": "Updated the system"
        })
    else:
        return flask.jsonify({
            "success": False,
            "message": "Unknown command"
        })
        
@app.route("/start", methods=["POST"])
def start():
    """
    Start the AstroPi imaging session
    """
    camera = picamera.PiCamera()
    
    # Configure the camera
    if params["iso"] == constants.AUTO:
        params["iso"] = "auto"
    camera.iso = params["iso"]
    
    if params["focus"] == constants.AUTO:
        params["focus"] = "auto"
    elif params["focus"] == constants.INFINITY:
        params["focus"] = "infinity"
    camera.exposure_mode = params["focus"]
    
    if params["image_denoise"] == 0:
        camera.image_denoise = False
    else:
        camera.image_denoise = True
    
    camera.brightness = params["brightness"]
    camera.contrast = params["contrast"]
    camera.exposure_compensation = params["exposure_compensation"]
    camera.sharpness = params["sharpness"]
    camera.shutter_speed = params["exposure"]
    camera.resolution = (params["resolution_x"], params["resolution_y"])
    
    awb_modes = camera.AWB_MODES
    camera.awb_mode = awb_modes[params["awb_mode"]]
    exposure_modes = camera.EXPOSURE_MODES
    camera.exposure_mode = exposure_modes[params["exposure_mode"]]
    flash_modes = camera.FLASH_MODES
    camera.flash_mode = flash_modes[params["flash_mode"]]
    metering_modes = camera.METER_MODES
    camera.meter_mode = metering_modes[params["metering_mode"]]
    drc_strengths = camera.DRC_STRENGTHS
    camera.drc_strength = drc_strengths[params["drc_strength"]]

    camera.zoom = (params["zoom_x"], params["zoom_y"], params["zoom_w"], params["zoom_h"])
    camera.color_effects = (params["color_effect_u"], params["color_effect_v"])
    
    # Start the imaging session
    log("Starting the imaging session")
    camera.start_preview()
    for i in range(params["image_count"]):
        camera.capture(f"../Images/{i}.jpg")
        log(f"Captured image {i}")
        requests.post(f"http://{client_ip}:{constants.ASTROPI_CLIENT_PORT}/state_update", data={
            "image_count": i
        })
    return flask.jsonify({
        "success": True,
        "message": "Started the AstroPi imaging session"
    })
    
# Run the Flask app
if __name__ == "__main__":
    os.system("ifconfig")
    app.run(port=constants.ASTROPI_PORT, debug=True, host="0.0.0.0")
