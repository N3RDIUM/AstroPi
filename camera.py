# NOTE: This is for non-pi devices only!
from uuid import uuid4
import shutil
import os
import time
import picamera2

SETTINGS = set([
    'exposure',
    'iso'
])

class Camera:
    def __init__(self, logger) -> None:
        self.written = 0
        self.logger = logger
        self.camera = picamera2.Picamera2()
        self.config = self.camera.create_still_configuration(main={}, raw={})
        self.settings = {
            'exposure': 1000, # in ms
            'iso': 100
        }
        self.init = False
        
    def initialise_camera(self):
        self.camera.start(show_preview=False)
        self.init = True
        
    def release(self):
        self.camera.stop()
    
    def step_preview(self):
        shutil.rmtree('static/preview')
        os.makedirs('static/preview')
        
        impath = "static/preview/" + str(self.written) + str(uuid4()) + ".png"
        self.camera.configure(self.config)
        self.camera.set_controls({
            "ExposureTime": self.settings['exposure'], 
            "AnalogueGain": self.settings['iso'] * 100
        })
        self.camera.capture_file(impath)
        
        self.written += 1
        
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
        
        self.logger.info(f'[internals/_camera] Setting {key} is now {value}!')
        return '[OK]'