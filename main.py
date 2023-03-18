# imports
from PyQt5 import QtWidgets, uic
import boardcon
import logging
import time
import json
import sys
import os

# Import constants
import Pi.constants as constants

# If the log file already exists, delete it
if os.path.exists("log.txt"):
    os.remove("log.txt")
logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

class AstroPi(QtWidgets.QMainWindow):
    """
    The main window of the AstroPi application
    """
    def __init__(self):
        """
        Initialize the main window
        """
        super(AstroPi, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('./UI/MainWindow.ui', self) # Load the .ui file
        
        # Log success
        self.log("<strong>AstroPi v2023.0.12</strong>")
        self.log("AstroPi has started successfully!")
        
        self.show() # Show the GUI
        
        # Set the background image of the window as the AstroPi logo
        self.label_17.setStyleSheet("""background-image: url(\"./assets/AstroPi.png\"); 
                                    background-repeat: no-repeat; 
                                    background-position: center; 
                                    background-color: black;""")
        # self.setStyleSheet("background-color: black;")
        
        # Add click callbacks to the buttons
        self.toolButton.clicked.connect(self.clearLog)
        self.toolButton_2.clicked.connect(self.saveLog)
        self.pushButton_7.clicked.connect(self.setSaveDir)
        self.pushButton.clicked.connect(self.connect)
        self.pushButton_2.clicked.connect(self.pullUpdates)
        self.pushButton_3.clicked.connect(self.systemUpdate)
        self.pushButton_6.clicked.connect(self.startSession)
        
        # Add callback to slider
        self.horizontalSlider.valueChanged.connect(self.setProcessorFanSpeed)
        self.horizontalSlider_2.valueChanged.connect(self.setSensorFanSpeed)
        self.horizontalSlider_3.valueChanged.connect(self.setISO)
        self.horizontalSlider_4.valueChanged.connect(self.setFocus)
        self.horizontalSlider_5.valueChanged.connect(self.setBrightness)
        self.horizontalSlider_6.valueChanged.connect(self.setContrast)
        self.horizontalSlider_7.valueChanged.connect(self.setExposureCompensation)
        self.horizontalSlider_8.valueChanged.connect(self.setSharpness)
        
        # Add callbacks to line edits
        self.lineEdit_2.editingFinished.connect(self.setImageCount)
        self.lineEdit_3.editingFinished.connect(self.setInterval)
        self.lineEdit_4.editingFinished.connect(self.setExposure)
        self.lineEdit_13.editingFinished.connect(self.setEffect_config)
        self.lineEdit_9.editingFinished.connect(self.setColorEffectU)
        self.lineEdit_10.editingFinished.connect(self.setColorEffectV)
        self.lineEdit_14.editingFinished.connect(self.setZoomX)
        self.lineEdit_15.editingFinished.connect(self.setZoomY)
        self.lineEdit_16.editingFinished.connect(self.setZoomW)
        self.lineEdit_17.editingFinished.connect(self.setZoomH)
        self.lineEdit_7.editingFinished.connect(self.setResolutionW)
        self.lineEdit_8.editingFinished.connect(self.setResolutionH)
        
        # Add callbacks to combo boxes
        self.comboBox.currentIndexChanged.connect(self.setSessionTime)
        self.comboBox_2.currentIndexChanged.connect(self.setProcessorFanState)
        self.comboBox_3.currentIndexChanged.connect(self.setCameraFanState)
        self.comboBox_4.currentIndexChanged.connect(self.setTransferQuality)
        self.comboBox_5.currentIndexChanged.connect(self.setAWBMode)
        self.comboBox_6.currentIndexChanged.connect(self.setDRCStrength)
        self.comboBox_7.currentIndexChanged.connect(self.setExposureMode)
        self.comboBox_8.currentIndexChanged.connect(self.setImageDenoise)
        self.comboBox_9.currentIndexChanged.connect(self.setFlashMode)
        self.comboBox_11.currentIndexChanged.connect(self.setMeteringMode)
        self.comboBox_10.currentIndexChanged.connect(self.setImageEffect)
        
        # Set default values to variables
        self.save_dir = None
        self.comms = None
        
    def resizeEvent(self, event):
        """
        On resize event
        """
        # Get the new size of the window
        size = self.size()
        # Get the current width and height of the window
        width = size.width()
        height = size.height()
        
        # Get the new width of the window
        new_width = width - 330
        
        # Set the size and location of the widgets
        self.label_17.resize(new_width, height - 160)
        self.tabWidget.resize(330, height)
        self.tabWidget.move(new_width, 0)
        self.textEdit.resize(new_width, 90)
        self.textEdit.move(0, height - 150)
        self.toolButton.move(new_width - 64, height - 150)
        self.toolButton.resize(32, 32)
        self.toolButton_2.move(new_width - 64, height - 118)
        self.toolButton_2.resize(32, 32)
        
        # Log the new size of the window
        self.log("Window resized to: " + str(width) + "x" + str(height), logging.DEBUG)
        
    def log(self, text, level=logging.INFO):
        """
        Log text to the textEdit
        """
        # Get timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # Set text color based on logging level
        if level == logging.INFO:
            color = "green"
        elif level == logging.WARNING:
            color = "yellow"
        elif level == logging.ERROR:
            color = "red"
        elif level == logging.DEBUG:
            color = "white"
        else:
            color = "blue"
        # Write text to the textEdit
        self.textEdit.append(f"<font color=\"{color}\">{timestamp} [{logging.getLevelName(level)}] " + text + "</font>")
        # Write text to the log file
        if level == logging.INFO:
            logging.info(text)
        elif level == logging.WARNING:
            logging.warning(text)
        elif level == logging.ERROR:
            logging.error(text)
        elif level == logging.DEBUG:
            logging.debug(text)
        print(f"{timestamp} [{logging.getLevelName(level)}] " + text)
        
    def clearLog(self):
        """
        Clear the textEdit
        """
        self.textEdit.clear()
        
    def saveLog(self):
        """
        Save the textEdit to a file
        """
        try:
            # Create a file dialog
            fileDialog = QtWidgets.QFileDialog()
            fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
            
            # Set the file dialog to only accept .txt files
            fileDialog.setNameFilter("Text files (*.txt)")
            # Set the default file name
            fileDialog.selectFile("log.txt")
            
            # Show the file dialog
            fileDialog.exec_()
            
            # Get the selected file name
            fileName = fileDialog.selectedFiles()[0]
            with open(fileName, "w") as f:
                f.write(self.textEdit.toPlainText())
        except IndexError:
            # No file was selected
            self.log("No file was selected", logging.WARNING)
        except Exception as e:
            self.log("Error saving log: " + str(e), logging.ERROR)
            
    def pullUpdates(self):
        if self.comms:
            self.comms.system(constants.PULL_UPDATES)
            self.log("Pulling updates", logging.INFO)
        else:
            self.log("No connection to the camera", logging.WARNING)
            
    def systemUpdate(self):
        if self.comms:
            self.comms.system(constants.SYSTEM_UPDATE)
            self.log("Updating system", logging.INFO)
        else:
            self.log("No connection to the camera", logging.WARNING)
            
    def setProcessorFanSpeed(self, speed):
        """
        Set the processor fan speed
        """
        speed = round(speed / 99 * 100)
        if speed == 0:
            self.label_19.setText("Auto")
            self.log("Processor fan speed set to Auto", logging.DEBUG)
            self.processor_fan_speed = constants.AUTO
        else:
            self.label_19.setText(str(speed) + "%")
            self.processor_fan_speed = speed
        if self.comms:
            self.comms.set("processor_fan_speed", self.processor_fan_speed)
    
    def setSensorFanSpeed(self, speed):
        """
        Set the sensor fan speed
        """
        speed = round(speed / 99 * 100)
        if speed == 0:
            self.label_20.setText("Auto")
            self.log("Sensor fan speed set to Auto", logging.DEBUG)
            self.sensor_fan_speed = constants.AUTO
        else:
            self.label_20.setText(str(speed) + "%")
            self.sensor_fan_speed = speed
        if self.comms:
            self.comms.set("sensor_fan_speed", self.sensor_fan_speed)
        
    def setISO(self, iso):
        """
        Set the ISO
        """
        iso = round(iso / 99 * 1500) + 100
        self.label_23.setText(str(iso))
        self.iso = iso
        if self.comms:
            self.comms.set("iso", self.iso)
        
    def setFocus(self, focus):
        """
        Set the focus
        """
        if focus == 0:
            self.label_26.setText("Auto")
            self.focus = constants.AUTO
            self.log("Focus set to Auto", logging.DEBUG)
        elif focus == 99:
            self.label_26.setText("Infinity")
            self.focus = constants.INFINITY
            self.log("Focus set to Infinity", logging.DEBUG)
        else:
            self.label_26.setText(str(focus))
            self.focus = focus
        if self.comms:
            self.comms.set("focus", self.focus)
            
    def setSaveDir(self):
        """
        Open a file dialog to select a directory to save images to
        """
        dialog = QtWidgets.QFileDialog()
        dialog.create()
        dir = dialog.getExistingDirectory()

        while dialog.isVisible():
            QtWidgets.QApplication.processEvents()
        
        if os.path.isdir(dir):
            self.save_dir = dir
            self.lineEdit_5.setText(dir)
            self.log("Save directory set to: " + dir, logging.INFO)
        
        dialog.close()
        
    def connect(self):
        """
        Connect to the AstroPi
        """
        try:
            # Get the IP address
            ip = self.lineEdit.text()
            self.comms = boardcon.AstroPiBoard(ip, self)
            self.comms.connect()
            self.log("Connected to AstroPi at " + ip, logging.INFO)
            self.pushButton.setEnabled(False)
        except Exception as e:
            self.log("Error connecting to AstroPi: " + str(e), logging.ERROR)
            self.comms.set_state(constants.DISCONNECTED)
            self.comms.kill_server()
            
    # # On window close
    # def closeEvent(self, event):
    #     """
    #     On window close
    #     """
    #     # Close the connection to the AstroPi
    #     if self.comms:
    #         self.comms.terminate()
    #     # Close the log file
    #     logging.shutdown()
    #     # Close the window
    #     event.accept()
    #     # Exit the program
    #     sys.exit()

    def setBrightness(self, brightness):
        """
        Set the brightness
        """
        brightness = round(brightness / 99 * 100)
        self.label_45.setText(str(brightness))
        self.brightness = brightness
        if self.comms:
            self.comms.set("brightness", self.brightness)
    
    def setContrast(self, contrast):
        """
        Set the contrast
        """
        contrast = round(contrast / 99 * 200) - 100
        self.label_49.setText(str(contrast))
        self.contrast = contrast
        if self.comms:
            self.comms.set("contrast", self.contrast)
            
    def setExposureCompensation(self, compensation):
        """
        Set the exposure compensation
        """
        compensation = round(compensation / 99 * 50) - 25
        self.label_54.setText(str(compensation))
        self.exposure_compensation = compensation
        if self.comms:
            self.comms.set("exposure_compensation", self.exposure_compensation)
            
    def setSharpness(self, sharpness):
        """
        Set the sharpness
        """
        sharpness = round(sharpness / 99 * 200) - 100
        self.label_65.setText(str(sharpness))
        self.sharpness = sharpness
        if self.comms:
            self.comms.set("sharpness", self.sharpness)
            
    def setImageCount(self):
        """
        Set the image counter
        """
        if self.comms:
            self.comms.set("image_count", self.lineEdit_2.text())
            
    def setInterval(self):
        """
        Set the interval
        """
        if self.comms:
            self.comms.set("interval", self.lineEdit_3.text())
        
    def setExposure(self):
        """
        Set the exposure numerator
        """
        if self.comms:
            self.comms.set("exposure", self.lineEdit_4.text())
            
    def setEffect_config(self):
        """
        Set the effect parameters
        """
        try:
            effect__config = json.loads(self.lineEdit_13.text())
        except:
            effect__config = {}
            self.log("Invalid JSON for effect parameters", logging.ERROR)
        if self.comms:
            self.comms.set("effect__config", effect__config)
        
    def setColorEffectU(self):
        """
        Set the color effect U
        """
        if self.comms:
            self.comms.set("color_effect_u", self.lineEdit_9.text())
        
    def setColorEffectV(self):
        """
        Set the color effect V
        """
        if self.comms:
            self.comms.set("color_effect_v", self.lineEdit_10.text())
        
    def setZoomX(self):
        """
        Set the zoom X
        """
        if self.comms:
            self.comms.set("zoom_x", self.lineEdit_14.text())
        
    def setZoomY(self):
        """
        Set the zoom Y
        """
        if self.comms:
            self.comms.set("zoom_y", self.lineEdit_15.text())

    def setZoomW(self):
        """
        Set the zoom W
        """
        if self.comms:
            self.comms.set("zoom_w", self.lineEdit_16.text())
            
    def setZoomH(self):
        """
        Set the zoom H
        """
        if self.comms:
            self.comms.set("zoom_h", self.lineEdit_17.text())
            
    def setResolutionW(self):
        """
        Set the resolution width
        """
        if self.comms:
            self.comms.set("resolution_x", self.lineEdit_7.text())
            
    def setResolutionH(self):
        """
        Set the resolution height
        """
        if self.comms:
            self.comms.set("resolution_x", self.lineEdit_8.text())
            
    def setSessionTime(self, time):
        if self.comms:
            self.comms.set("session_time", time)

    def setProcessorFanState(self, state):
        """
        Set the processor fan state
        """
        if self.comms:
            self.comms.set("processor_fan_state", state)
            
    def setCameraFanState(self, state):
        """
        Set the camera fan state
        """
        if self.comms:
            self.comms.set("camera_fan_state", state)
            
    def setTransferQuality(self, quality):
        """
        Set the transfer quality
        """
        if self.comms:
            self.comms.set("transfer_quality", quality)
            
    def setAWBMode(self, mode):
        """
        Set the AWB mode
        """
        if self.comms:
            self.comms.set("awb_mode", mode)
            
    def setDRCStrength(self, strength):
        """
        Set the DRC strength
        """
        if self.comms:
            self.comms.set("drc_strength", strength)
            
    def setExposureMode(self, mode):
        """
        Set the exposure mode
        """
        if self.comms:
            self.comms.set("exposure_mode", mode)
            
    def setFlashMode(self, mode):
        """
        Set the flash mode
        """
        if self.comms:
            self.comms.set("flash_mode", mode)
            
    def setImageDenoise(self, denoise):
        """
        Set the image denoise
        """
        if self.comms:
            self.comms.set("image_denoise", denoise)
        
    def setMeteringMode(self, mode):
        """
        Set the metering mode
        """
        if self.comms:
            self.comms.set("metering_mode", mode)
        
    def setImageEffect(self, effect):
        """
        Set the image effect
        """
        if self.comms:
            self.comms.set("image_effect", effect)
            
    def startSession(self):
        """
        Start the session!
        """
        if not self.comms:
            self.log("No comms. Please connect your AstroPi.", logging.ERROR)
            return
        if not self.comms.eval_settings():
            self.log("Settings not evaluated", logging.ERROR)
            return
        self.comms.start_session()
        
if __name__ == "__main__":
    # Create an instance of QtWidgets.QApplication
    app = QtWidgets.QApplication(sys.argv)
    # Show the GUI
    window = AstroPi()
    # Execute the main loop
    app.exec_()
    # Exit the application
    if window.comms:
        window.comms.terminate()
    sys.exit()