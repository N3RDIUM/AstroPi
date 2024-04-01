# NOTE: This is for non-pi devices only!
from uuid import uuid4
from threading import Lock
import picamera2
import time
from PIL import Image
import rawpy

def convert_dng_to_jpg(input_dng_file, output_jpg_file):
    with rawpy.imread(input_dng_file) as raw:
        rgb = raw.postprocess(
            use_camera_wb=True,
            output_color=rawpy.ColorSpace.sRGB,
        )
    image = Image.fromarray(rgb)
    image.save(output_jpg_file, format='JPEG', quality=100)


SETTINGS = set([
    'exposure',
    'iso'
])

class Camera:
    def __init__(self, logger) -> None:
        self.logger = logger
        self.camera = picamera2.Picamera2()
        self.config = self.camera.create_still_configuration(main={}, raw={})
        self.settings = {
            'exposure': 1000, # in ms
            'iso': 100
        }
        self.refresh_controls()
        self.init = False
        self.camera_lock = Lock()
        
    def initialise_camera(self):
        self.camera.start()
        self.init = True
        
    def release(self):
        self.camera.stop()
        
    def refresh_controls(self):
        with self.camera.controls as ctrl:
            ctrl.AnalogueGain = int(self.settings['iso']) / 100
            ctrl.ExposureTime = int(self.settings['exposure'])
    
    def step_preview(self):
        impath = "static/preview/" + str(uuid4()) + ".png"
            
        self.camera.start()
        time.sleep(1 / 60)
        self.refresh_controls()
        time.sleep(1 / 60)
        self.camera.capture_file(impath)
        time.sleep(1 / 60)
        self.camera.stop()
        time.sleep(1 / 60)
        
        return '../' + impath
    
    def capture(self):
        impath = "static/captured/" + str(time.time()) + ".dng"
        if self.init:
            self.release()
        
        self.initialise_camera()
        time.sleep(1 / 60)
        self.refresh_controls()
        time.sleep(1 / 60)
        self.camera.capture_file(impath, 'raw')
        time.sleep(1 / 60)
        self.release()
        time.sleep(1 / 60)
        
        self.logger.info(f'[internals/_camera] Converting DNG to JPG for preview: {impath}')
        convert_dng_to_jpg(impath, impath.removesuffix('.dng') + '.jpg')
        
        return '../' + impath
    
    def setting(self, key, value):
        if not key in SETTINGS:
            self.logger.error(f'[internals/_camera] No such setting: {key}')
            return f'[!!]'
        if key == 'exposure':
            try:
                value = float(value)
                if value <= 0:
                    self.logger.error(f'[internals/_camera] Expected value > 0 for {key}, got {value}')
                    return f'[!!]'
                self.settings[key] = value
            except:
                self.logger.error(f'[internals/_camera] Cannot convert to float for {key}: {value}')
                return f'[!!]'
        if key == 'iso':
            try:
                value = int(value)
                if value <= 0:
                    self.logger.error(f'[internals/_camera] Expected natural number for {key}, got {value}')
                    return f'[!!]'
                self.settings[key] = value
            except:
                self.logger.error(f'[internals/_camera] Cannot convert to natural number: {value}')
                return f'[!!]'
        
        self.refresh_controls()
        
        self.logger.info(f'[internals/_camera] Setting {key} is now {value}!')
        return '[OK]'