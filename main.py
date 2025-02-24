import logging
import os
import shutil
import sys
import uuid

from flask import Flask, render_template, request

from camera import Camera

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

os.makedirs('static/preview', exist_ok=True)
os.makedirs('static/captured', exist_ok=True)
os.makedirs('static/captured-raw', exist_ok=True)
os.makedirs('static/archives', exist_ok=True)

cam = Camera(logger)
app = Flask(__name__)
flasklog = logging.getLogger('werkzeug')
flasklog.disabled = True

logger.info(r'''
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log')
def log():
    return render_template('log.html')

@app.route('/preview')
def preview():
    return render_template('preview.html')

@app.route('/capture')
def capture():
    return render_template('capture.html')

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/preview-step')
def preview_step():
    impath = cam.step_preview()
    return impath

@app.route('/capture-step')
def capture_step():
    impath = cam.capture()
    return impath

@app.route('/stop')
def stop():
    # cam.release()
    return 'Success!'

@app.route('/start')
def start():
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

@app.route('/prepare-download')
def prepare_download(): # TODO: This is impractical.
    outfile = f'static/archives/{uuid.uuid4()}'
    logger.log(logging.INFO, f"[internals/prepare-download] Archiving static/captured into {outfile}")
    shutil.make_archive(outfile, 'zip', 'static/captured-raw')
    logger.log(logging.INFO, "[internals/prepare-download] Archive created successfully! Returning link to client...")
    return '../' + outfile + '.zip'

def main():
    try:
        app.run(host="0.0.0.0", port=8080, debug=False)
    except Exception as e:
        cam.release()
        print(f'Exited due to exception {e}. The camera was released successfully.')

if __name__ == "__main__":
    main()
