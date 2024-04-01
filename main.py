
from flask import Flask, render_template, request
from camera import Camera
import shutil
import os
import logging
import sys

if os.path.exists('astropi.log'): os.remove('astropi.log')

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('astropi.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

if not os.path.exists('static/preview'):
    os.makedirs('static/preview')
else: 
    shutil.rmtree('static/preview')
    os.makedirs('static/preview')
    
if not os.path.exists('static/captured'):
    os.makedirs('static/captured')
else: 
    shutil.rmtree('static/captured')
    os.makedirs('static/captured')
    
cam = Camera(logger)
app = Flask(__name__)
flasklog = logging.getLogger('werkzeug')
flasklog.disabled = True

logger.info('''
 __________________________________________________________________________________________________________________
|   /$$$$$$              /$$                         /$$$$$$$  /$$ | AstroPi v0.1-alpha                            |
|  /$$__  $$            | $$                        | $$__  $$|__/ | Welcome to AstroPi v0.1-alpha!                |
| | $$  \ $$  /$$$$$$$ /$$$$$$    /$$$$$$   /$$$$$$ | $$  \ $$ /$$ | This is a very early version of the software, |
| | $$$$$$$$ /$$_____/|_  $$_/   /$$__  $$ /$$__  $$| $$$$$$$/| $$ | so expect bugs and missing features.          |
| | $$__  $$|  $$$$$$   | $$    | $$  \__/| $$  \ $$| $$____/ | $$ | If you find any bugs,                         |
| | $$  | $$ \____  $$  | $$ /$$| $$      | $$  | $$| $$      | $$ | please report them on GitHub Issues:          |
| | $$  | $$ /$$$$$$$/  |  $$$$/| $$      |  $$$$$$/| $$      | $$ | https://github.com/n3rdium/AstroPi/issues     |
| |__/  |__/|_______/    \___/  |__/       \______/ |__/      |__/ | CLEAR SKIES!                                  |
|__________________________________________________________________________________________________________________|
''')

@app.route('/log')
def log():
    return render_template('log.html')

@app.route('/preview')
def preview():
    return render_template('preview.html')

@app.route('/capture')
def capture():
    return render_template('capture.html')

@app.route('/preview-step')
def preview_step():
    try:
        impath = cam.step_preview()
        return impath
    except:
        return '../static/assets/AstroPi.png`'
    
@app.route('/capture-step')
def capture_step():
    try:
        impath = cam.capture()
        return impath
    except:
        return '../static/assets/AstroPi.png`'

@app.route('/stop')
def stop():
    # Lets keep this here for some reason
    # Yes, the /preview page still fetches /stop!
    # cam.release()
    return 'Success!'

@app.route('/start')
def start(): 
    # Lets keep this here for some reason
    # Yes, the /preview page still fetches /start!
    # cam.initialise_camera()
    return 'Success!'

@app.route('/logs')
def logs():
    with open('astropi.log', 'r') as f:
        logs = f.read()
    return logs

LEVELS_MAP = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    'fatal': logging.FATAL
}
@app.route('/add-log', methods=['POST'])
def addLog():
    params = request.get_json()
    msg = params['msg']
    lvl = params['lvl']
    level = LEVELS_MAP[str(lvl)]
    logger.log(level, str(msg))
    return 'Success!'

@app.route('/settings', methods=['POST'])
def settings():
    params = request.get_json()
    key = params['key']
    value = params['value']
    return cam.setting(key, value)

def main():
    try:
        app.run(host="0.0.0.0", port=8080, debug=False)
    except Exception as e:
        cam.release()
        print(f'Exited due to exception {e}. The camera was released successfully.')

if __name__ == "__main__":
    main()