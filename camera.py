import zmq
import sys
import logging
from picamera2 import Picamera2

# Init logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s [CAMERA] %(message)s')

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
socket = context.socket(zmq.REQ)
_ = socket.connect("tcp://*:8081")

# Init camera
camera = Picamera2()
camera.start()

