# imports
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import boardcon
import logging
import time
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
        self.preview.setStyleSheet("""background-image: url(\"./assets/AstroPi.png\"); 
                                    background-repeat: no-repeat; 
                                    background-position: center; 
                                    background-color: black;""")
        
        # Add click callbacks to the buttons
        self.toolButton.clicked.connect(self.clearLog)
        self.toolButton_2.clicked.connect(self.saveLog)
        self.SaveDirBrowse.clicked.connect(self.setSaveDir)
        self.EnterBoardIP.clicked.connect(self.connect)
        self.PullUpdates.clicked.connect(self.pullUpdates)
        self.SystemUpdate.clicked.connect(self.systemUpdate)
        self.StartButton.clicked.connect(self.startSession)
        
        # Add callbacks to sliders
        self.ExposureValue.valueChanged.connect(self.setExposureValue)
        self.LensPosition.valueChanged.connect(self.setLensPosition)
        self.Gain.valueChanged.connect(self.setGain)
        
        # Add callbacks to line edits
        self.NumImages.editingFinished.connect(self.setImageCount)
        self.ImageInterval.editingFinished.connect(self.setInterval)
        self.ExposureTime.editingFinished.connect(self.setExposure)
        
        # Add callbacks to combo boxes
        self.TransferQuality.currentIndexChanged.connect(self.setTransferQuality)
        self.NoiseReductionMode.currentIndexChanged.connect(self.setNoiseReductionMode)
        
        # Set default values to variables
        self.save_dir = None
        self.comms = None
        
        # Set the default values of the widgets
        self.ExposureTime.setText(str(1000000))
        self.ImageInterval.setText(str(0))
        self.NumImages.setText(str(1))
        self.ExposureValue.setValue(50)
        self.LensPosition.setValue(int(99/32))
        
        # Initialize a temporary object for config
        self.comms = boardcon.AstroPiBoard(None, self)
        
        # Start updates
        self.startUpdate()
        
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
            _tempconfig = self.comms._config.copy()
            self.comms = boardcon.AstroPiBoard(ip, self)
            self.comms.connect()
            self.comms._config = _tempconfig
            self.log("Connected to AstroPi at " + ip, logging.INFO)
            self.EnterBoardIP.setEnabled(False)
            time.sleep(2)
            self.showPreview()
        except Exception as e:
            self.log("Error connecting to AstroPi: " + str(e), logging.ERROR)
            self.comms.set_state(constants.DISCONNECTED)
            self.comms.kill_server()
    
    def showPreview(self):
        """
        Show the preview instead of the "No output" text
        """
        self.stream = QWebEngineView()
        self.stream.setUrl(QUrl(f"http://{self.comms.ip}:{constants.ASTROPI_PREVIEW_PORT}/"))
        self.preview.removeWidget(self.preview.currentWidget())
        self.preview.addWidget(self.stream)
        self.comms.set_imaging_state(constants.PREVIEW)
        
    def updateTable(self):
        """
        Update the table with the current values
        """
        _config = self.comms._config
        self.SettingsReview.setRowCount(len(_config))
        self.SettingsReview.setColumnCount(2)
        self.SettingsReview.setHorizontalHeaderLabels(["Setting", "Value"])
        for n, key in enumerate(sorted(_config.keys())):
            _key = key.replace("_", " ").title()
            self.SettingsReview.setItem(n, 0, QtWidgets.QTableWidgetItem(_key))
            self.SettingsReview.setItem(n, 1, QtWidgets.QTableWidgetItem(str(_config[key])))
            
    # Define signals
    progressSignal = QtCore.pyqtSignal(int)
    progressTextSignal = QtCore.pyqtSignal(str)
    cameraStatusSignal = QtCore.pyqtSignal(str)
    ETASignal = QtCore.pyqtSignal(str)
        
    def updateProgress(self, value):
        """
        Update the progress bar
        """
        self.progressSignal.emit(value)
        
    def updateProgressText(self, text):
        """
        Update the progress bar text
        """
        self.progressTextSignal.emit(text)
        
    def updateEta(self, eta):
        """
        Update the ETA
        """
        self.ETASignal.emit(f"ETA: {eta} seconds")
            
    def startUpdate(self):
        """
        Start automatically updating the progress and ETA
        """
        # Connect signals
        self.progressSignal.connect(self.ImagingProgress.setValue)
        self.progressTextSignal.connect(self.ImagingProgressText.setText)
        self.ETASignal.connect(self.ETAText.setText)
      
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
            
    def setExposureValue(self, value):
        """
        Set the exposure value.
        """
        value = (value / 99 * 16) - 8
        self.ExposureValueText.setText(str(round(value, 2)))
        if self.comms:
            self.comms.set("ExposureValue", value)
            
    def setLensPosition(self, position):
        """
        Set the lens position
        """
        position = (position / 99 * 32)
        if position==0:
            self.LensPositionText.setText("Inf")
            self.log("Lens position set to Infinity", logging.DEBUG)
        else:
            self.LensPositionText.setText(str(round(position, 2)))
        if self.comms:
            self.comms.set("LensPosition", position)
            
    def setGain(self, gain):
        """
        Set the analogue gain
        """
        gain = (gain / 99 * 15) + 1
        if gain==1:
            self.GainText.setText("Auto")
            self.log("Gain set to Auto", logging.DEBUG)
            if self.comms:
                self.comms.removeConfig("AnalogueGain")
        else:   
            self.GainText.setText(str(round(gain, 2)))
            if self.comms:
                self.comms.set("AnalogueGain", gain)
            
    def setTransferQuality(self, quality):
        """
        Set the transfer quality
        """
        if self.comms:
            self.comms.set("transfer_quality", quality)
    
    def setNoiseReductionMode(self, mode):
        """
        Set the noise reduction mode
        """
        if self.comms:
            self.comms.set("NoiseReductionMode", mode)
            
    def startSession(self):
        """
        Start the session!
        """
        self.comms.set_imaging_state(constants.IMAGING)
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
    app.exec()
    # Exit the application
    if window.comms:
        window.comms.terminate()
    sys.exit()