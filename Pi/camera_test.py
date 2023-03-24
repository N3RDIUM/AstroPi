print("[PiCamera2] Starting camera test...")
import time
from picamera2 import Picamera2

print("[PiCamera2] Configuring camera...")
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

print("[PiCamera2] Starting camera, warming up...")
picam2.start()
time.sleep(2)

# Start capturing images. FOREVER!
print("[PiCamera2] Starting capture...")
captured = 0
while True:
    # Capture DNG image
    r = picam2.capture_request(capture_config)
    r.save_dng(f"{captured}.dng")
    captured += 1
    print(f"[PiCamera2] Captured RAW {captured}.dng")
    r.release()
