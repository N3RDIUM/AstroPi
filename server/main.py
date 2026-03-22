import atexit

from flask import Flask, request, jsonify
from .camera import (
    Camera,
    CameraControls,
    IntervalometerControls,
    UpdateControls,
    UpdateIntervalomater,
    StartPreview,
    StartCapture,
    StopPreview,
    StopCapture
)


DEFAULT_EXPOSURE_TIME: int = 100000
DEFAULT_ANALOGUE_GAIN: float = 8.0
DEFAULT_COUNT: int = 1
DEFAULT_COOLDOWN: int = 1

app = Flask(__name__)
cam = Camera()
_ = atexit.register(cam.kill)

@app.route('/')
def home():
    return jsonify({
        "response": "hello world from astropi"
    }), 200

@app.route('/camera_controls/', methods=["POST"])
def cam_controls():
    controls = request.form

    configuration = CameraControls(
        ExposureTime = DEFAULT_EXPOSURE_TIME,
        AnalogueGain = DEFAULT_ANALOGUE_GAIN
    )

    if "exposure" in controls:
        try:
            configuration.ExposureTime = int(controls["exposure"])
        except Exception as e:
            return jsonify({
                "response": f"failed to set exposure: {e}"
            }), 500

    if "gain" in controls:
        try:
            configuration.AnalogueGain = float(controls["gain"])
        except Exception as e:
            return jsonify({
                "response": f"failed to set exposure: {e}"
            }), 500

    cam.submit_command(UpdateControls(
        controls = configuration
    ))

    return jsonify({
        "response": "success"
    }), 200

@app.route('/intervalometer_controls/', methods=["POST"])
def intervalometer_controls():
    controls = request.form

    configuration = IntervalometerControls(
        Count = DEFAULT_COUNT,
        Cooldown = DEFAULT_COOLDOWN
    )

    if "count" in controls:
        try:
            configuration.Count = int(controls["count"])
        except Exception as e:
            return jsonify({
                "response": f"failed to set count: {e}"
            }), 500

    if "cooldown" in controls:
        try:
            configuration.Cooldown = int(controls["cooldown"])
        except Exception as e:
            return jsonify({
                "response": f"failed to set cooldown: {e}"
            }), 500

    cam.submit_command(UpdateIntervalomater(
        controls = configuration
    ))

    return jsonify({
        "response": "success"
    }), 200

@app.route('/start-preview/')
def start_preview():
    cam.submit_command(StartPreview())

    return jsonify({
        "response": "success"
    }), 200

@app.route('/stop-preview/')
def stop_preview():
    cam.submit_command(StopPreview())

    return jsonify({
        "response": "success"
    }), 200

@app.route('/start-capture/')
def start_capture():
    cam.submit_command(StartCapture())

    return jsonify({
        "response": "success"
    }), 200

@app.route('/stop-capture/')
def stop_capture():
    cam.submit_command(StopCapture())

    return jsonify({
        "response": "success"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

