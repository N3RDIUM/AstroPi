import flask
import requests
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

global client_ip
client_ip = None
global config
userconfig = {}

@app.route("/connect", methods=["POST"])
def communicate():
    """
    Communicate with the AstroPi board
    """
    # Get the data from the request
    data = flask.request.form
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
    userconfig[key] = value
    
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
        "message": userconfig,
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

# Run the Flask app
if __name__ == "__main__":
    os.system("ifconfig")
    app.run(port=constants.ASTROPI_PORT, debug=True, host="0.0.0.0")
