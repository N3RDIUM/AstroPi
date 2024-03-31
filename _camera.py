# NOTE: This is for non-pi devices only!
from uuid import uuid4
import cv2
from PIL import Image
import shutil
import os

class Camera:
    def __init__(self) -> None:
        self.written = 0
        self.init = False
        
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
        
    def release(self):
        self.cap.release()