# NOTE: This is for non-pi devices only!
from uuid import uuid4
import shutil
import os
from threading import Lock
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
        self.camera_lock = Lock()
        
    def initialise_camera(self):
        self.camera_lock.acquire()
        self.camera.start(show_preview=False)
        self.init = True
        self.camera_lock.release()
        
    def release(self):
        self.camera_lock.acquire()
        self.camera.stop()
        self.camera_lock.release()
    
    def step_preview(self):
        shutil.rmtree('static/preview')
        os.makedirs('static/preview')
        
        impath = "static/preview/" + str(self.written) + str(uuid4()) + ".png"
        self.camera_lock.acquire()
        self.camera.capture_file(impath)
        self.camera_lock.release()
        
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
            
        self.camera_lock.acquire()
        self.release()
        self.camera.configure(self.config)
        self.camera.set_controls({
            "ExposureTime": self.settings['exposure'], 
            "AnalogueGain": self.settings['iso'] * 100
        })
        self.camera_lock.release()
        
        self.logger.info(f'[internals/_camera] Setting {key} is now {value}!')
        return '[OK]'