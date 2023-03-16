# imports
from PyQt5 import QtWidgets, uic
import logging
import time
import sys

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
        self.log("<strong>AstroPi v2023.0.1</strong>")
        self.log("AstroPi has started successfully!")
        
        self.show() # Show the GUI
        
        # Set the background image of the window as the AstroPi logo
        self.label_17.setStyleSheet("background-image: url(\"./assets/AstroPi.png\"); background-repeat: no-repeat; background-position: center; background-color: black;")
        self.setStyleSheet("background-color: black;")
        
        # Add click callbacks to the buttons
        self.toolButton.clicked.connect(self.clearLog)
        self.toolButton_2.clicked.connect(self.saveLog)
        
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
        self.toolButton.move(new_width - 32, height - 150)
        self.toolButton.resize(32, 32)
        self.toolButton_2.move(new_width - 32, height - 118)
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

if __name__ == "__main__":
    # Create an instance of QtWidgets.QApplication
    app = QtWidgets.QApplication(sys.argv)
    # Show the GUI
    window = AstroPi()
    # Execute the main loop
    sys.exit(app.exec_())