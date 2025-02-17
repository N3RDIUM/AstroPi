import sys
import zmq
import logging
from flask import Flask

# Init logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('astropi.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

# Init 0mq
logger.log(logging.DEBUG, "[main] Initializing 0mq")
context = zmq.Context()
socket = context.socket(zmq.REP)
_ = socket.bind("tcp://*:8081")

# Init flask
logger.log(logging.DEBUG, "[main] Initializing Flask")
app = Flask(__name__)
flasklog = logging.getLogger('werkzeug')
flasklog.disabled = True

# Flask routes
@app.route("/")
def root():
    return "AstroPi Rewrite"

# Driver
if __name__ == "__main__":
    logger.log(logging.INFO, "[main] Running flask server on host 0.0.0.0 port 8080")
    app.run(host="0.0.0.0", port=8080, debug=False)

