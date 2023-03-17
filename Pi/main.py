import flask
import requests
import os
import logging
import socket
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
    with open("PiLog.txt", "r") as f:
        log = f.read()
    last_line = log.splitlines()[-1]
    print(last_line)

# Get the ifconfig ip address
ip = os.popen("ifconfig").read().split("inet ")[1].split(" ")[0]
log(f"Device IP: {ip}")
log(f"Device port: {constants.ASTROPI_PORT}")

# Create the Flask app
app = flask.Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def communicate():
    """
    Communicate with the computer
    """
    if flask.request.method == "GET":
        return "Hello from the AstroPi board!"
    # Get the data from the request
    data = flask.request.get_json()
    cmd_type = data["command"]
    print(cmd_type)
    if cmd_type == "connect":
        log("Board connected!")
        return flask.jsonify({"status": "connected"})

# Run the Flask app
if __name__ == "__main__":
    os.system("ifconfig")
    app.run(port=constants.ASTROPI_PORT, debug=True, host="0.0.0.0")
