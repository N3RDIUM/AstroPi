# NOTE: This is for non-pi devices only!
from uuid import uuid4
import cv2
from PIL import Image
import shutil
import os

SETTINGS = set([
    'exposure',
    'exposure-unit',
    'iso'
])
class Camera:
    def __init__(self, logger) -> None:
        self.written = 0
        self.logger = logger
        self.init = False
        self.settings = {
            'exposure': 1000, # in ms
            'exposure-unit': 'Milliseconds',
            'iso': 100
        }
        
    def initialise_camera(self):
        self.init = True
        self.cap = cv2.VideoCapture(0)
        
    def step_preview(self):
        shutil.rmtree('static/preview')
        os.makedirs('static/preview')
        
        ret, frame = self.cap.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        img = Image.fromarray(rgb)
        impath = "static/preview/" + str(self.written) + str(uuid4()) + ".png"
        img.save(impath)
        
        self.written += 1
        
        return '../' + impath
    
    def setting(self, key, value):
        if not key in SETTINGS:
            self.logger.error(f'[! NOT ON A PI] [internals/_camera] No such setting: {key}')
            return f'[!!]'
        if key == 'exposure':
            try:
                value = float(value)
                if value <= 0:
                    self.logger.error(f'[! NOT ON A PI] [internals/_camera] Expected value > 0 for {key}, got {value}')
                    return f'[!!]'
                self.settings[key] = value
            except:
                self.logger.error(f'[! NOT ON A PI] [internals/_camera] Cannot convert to float for {key}: {value}')
                return f'[!!]'
        if key == 'exposure-unit':
            value = str(value)
            self.settings[key] = value
        if key == 'iso':
            try:
                value = int(value)
                if value <= 0:
                    self.logger.error(f'[! NOT ON A PI] [internals/_camera] Expected natural number for {key}, got {value}')
                    return f'[!!]'
                self.settings[key] = value
            except:
                self.logger.error(f'[! NOT ON A PI] [internals/_camera] Cannot convert to natural number: {value}')
                return f'[!!]'
        self.logger.info(f'[! NOT ON A PI] [internals/_camera] Setting {key} is now {value}!')
        return '[OK]'
        
    def release(self):
        self.cap.release()