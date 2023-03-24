import time
from picamera2 import Picamera2

picam2 = Picamera2()
capture_config = picam2.create_still_configuration(
    raw={
        "size": (4608, 2592),    
    },
    controls={
        'ExposureTime': 12000000,
        'LensPosition': 0.0,
        'AnalogueGain': 8.0,
    }
)

picam2.start()
time.sleep(2)

# Start capturing images. FOREVER!
captured = 0
while True:
    buffers, metadata = picam2.capture_buffers(capture_config, ["raw"])
    picam2.helpers.save_dng(buffers[0], metadata, capture_config["raw"], f"{captured}.dng")
    captured += 1
