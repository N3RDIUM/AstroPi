
from flask import Flask, render_template
import logging

logging.basicConfig(
    format='%(message)s', 
    filename='astropi.log'
)

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True

logging.log(logging.INFO, ''' __________________________________________________________________________________________________________________
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
def home():
    return render_template('index.html')

@app.route('/logs')
def logs():
    with open('astropi.log', 'r') as f:
        logs = f.read()
    return logs

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)