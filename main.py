# imports
from PyQt5 import QtWidgets, uic
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
        self.label_17.setStyleSheet("""background-image: url(\"./assets/AstroPi.png\"); 
                                    background-repeat: no-repeat; 
                                    background-position: center; 
                                    background-color: black;""")
        self.setStyleSheet("background-color: black;")
        
        # Add click callbacks to the buttons
        self.toolButton.clicked.connect(self.clearLog)
        self.toolButton_2.clicked.connect(self.saveLog)
        self.pushButton_7.clicked.connect(self.setSaveDir)
        self.pushButton.clicked.connect(self.connect)
        
        # Add callback to slider
        self.horizontalSlider.valueChanged.connect(self.setProcessorFanSpeed)
        self.horizontalSlider_2.valueChanged.connect(self.setSensorFanSpeed)
        self.horizontalSlider_3.valueChanged.connect(self.setISO)
        self.horizontalSlider_4.valueChanged.connect(self.setFocus)
        
        # Set default values
        self.save_dir = None
        self.session_time_setting = 0
        self.processor_fan_speed = 0
        self.sensor_fan_speed = 0
        self.exposure = 0
        self.iso = 0
        self.focus = 0
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
            
    # On window close
    def closeEvent(self, event):
        """
        On window close
        """
        # Close the connection to the AstroPi
        if self.comms:
            try:
                self.comms.kill_server()
                self.log("Kill server command sent")
            except Exception as e:
                self.log("Error sending kill server command: " + str(e), logging.ERROR)
        # Close the log file
        logging.shutdown()
        sys.exit()

if __name__ == "__main__":
    # Create an instance of QtWidgets.QApplication
    app = QtWidgets.QApplication(sys.argv)
    # Show the GUI
    window = AstroPi()
    # Execute the main loop
    sys.exit(app.exec_())