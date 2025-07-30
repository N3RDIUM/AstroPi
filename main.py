import sys
import time
import logging
from flask import Flask, request
from picamera2 import Picamera2
from libcamera import controls
from threading import Lock

# Init logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s [MAIN] %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('astropi.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

# Init camera
camera = Picamera2()
lock = Lock()

config = camera.create_still_configuration()
camera.configure(config)

camera.start()

logger.info("Waiting for the camera to warm up...")
time.sleep(2)

# Some camera configuration
ctrl = {
    "AeEnable": False,
    "NoiseReductionMode": controls.draft.NoiseReductionModeEnum.Off,
    "AwbEnable": False,
    "ColourGains": (2.0, 2.0),
    "AnalogueGain": 20,
    "ExposureTime": int(60 * 1e6),
}
camera.set_controls(ctrl)
print(ctrl)

# Init flask
logger.log(logging.DEBUG, "[main] Initializing Flask")
app = Flask(__name__)
flasklog = logging.getLogger('werkzeug')
flasklog.disabled = True

# Flask routes
@app.route("/")
def root():
    return "AstroPi v0.0.1"

@app.route("/controls/", methods=["POST"])
def setting():
    ctrl.update(dict(request.form))

    lock.acquire()
    camera.set_controls(ctrl)
    lock.release()

    print(ctrl)

    return "success"

# Driver
if __name__ == "__main__":
    logger.log(logging.INFO, "[main] Running flask server on port 8080")
    app.run(host="0.0.0.0", port=8080, debug=False)

