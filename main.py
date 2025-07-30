import sys
import logging
from flask import Flask
from picamera2 import Picamera2

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

config = camera.create_still_configuration()
camera.configure(config)

camera.start()

# Init flask
logger.log(logging.DEBUG, "[main] Initializing Flask")
app = Flask(__name__)
flasklog = logging.getLogger('werkzeug')
flasklog.disabled = True

# Flask routes
@app.route("/")
def root():
    return "AstroPi v0.0.1"

@app.route("/settings/<str:name>", methods=["POST"])
def setting(name):
    print(name)
    return 200

# Driver
if __name__ == "__main__":
    logger.log(logging.INFO, "[main] Running flask server on port 8080")
    app.run(host="0.0.0.0", port=8080, debug=False)

