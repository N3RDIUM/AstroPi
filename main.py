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
        self.SaveDirBrowse.clicked.connect(self.setSaveDir)
        self.EnterBoardIP.clicked.connect(self.connect)
        self.PullUpdates.clicked.connect(self.pullUpdates)
        self.SystemUpdate.clicked.connect(self.systemUpdate)
        self.StartButton.clicked.connect(self.startSession)
        
        # Add callbacks to sliders
        self.ProcessorFanSpeed.valueChanged.connect(self.setProcessorFanSpeed)
        self.CameraFanSpeed.valueChanged.connect(self.setSensorFanSpeed)
        
        # Add callbacks to line edits
        self.NumImages.editingFinished.connect(self.setImageCount)
        self.ImageInterval.editingFinished.connect(self.setInterval)
        self.ExposureTime.editingFinished.connect(self.setExposure)
        
        # Add callbacks to combo boxes
        self.SessionTime.currentIndexChanged.connect(self.setSessionTime)
        self.ProcessorFanState.currentIndexChanged.connect(self.setProcessorFanState)
        self.CameraFanState.currentIndexChanged.connect(self.setCameraFanState)
        self.TransferQuality.currentIndexChanged.connect(self.setTransferQuality)
        
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
        # TODO: Add toggle button to enable/disable auto-scrolling
        self.textEdit.verticalScrollBar().setValue(self.textEdit.verticalScrollBar().maximum())
        
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
            self.ProcessorFanText.setText("Auto")
            self.log("Processor fan speed set to Auto", logging.DEBUG)
            processor_fan_speed = constants.AUTO
        else:
            self.ProcessorFanText.setText(str(speed) + "%")
            processor_fan_speed = speed
        if self.comms:
            self.comms.set("ProcessorFanSpeed", processor_fan_speed)
    
    def setSensorFanSpeed(self, speed):
        """
        Set the sensor fan speed
        """
        speed = round(speed / 99 * 100)
        if speed == 0:
            self.CameraFanText.setText("Auto")
            self.log("Sensor fan speed set to Auto", logging.DEBUG)
            sensor_fan_speed = constants.AUTO
        else:
            self.CameraFanText.setText(str(speed) + "%")
            sensor_fan_speed = speed
        if self.comms:
            self.comms.set("SensorFanSpeed", sensor_fan_speed)
            
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
            self.SaveDirInput.setText(dir)
            self.log("Save directory set to: " + dir, logging.INFO)
        
        dialog.close()
        
    def connect(self):
        """
        Connect to the AstroPi
        """
        try:
            # Get the IP address
            ip = self.BoardIP.text()
            self.comms = boardcon.AstroPiBoard(ip, self)
            self.comms.connect()
            self.log("Connected to AstroPi at " + ip, logging.INFO)
            self.EnterBoardIP.setEnabled(False)
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
      
    def setImageCount(self):
        """
        Set the image counter
        """
        if self.comms:
            self.comms.set("image_count", self.NumImages.text())
            
    def setInterval(self):
        """
        Set the interval
        """
        if self.comms:
            self.comms.set("interval", self.ImageInterval.text())
        
    def setExposure(self):
        """
        Set the exposure numerator
        """
        if self.comms:
            self.comms.set("ExposureTime", self.ExposureTime.text())

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