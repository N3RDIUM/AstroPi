# imports
from PyQt5 import QtWidgets, uic
import sys

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
        new_width = width - 330
        
        self.label_17.resize(new_width, height - 160)
        self.tabWidget.resize(330, height)
        self.tabWidget.move(new_width, 0)
        self.textEdit.resize(new_width, 160)
        self.textEdit.move(0, height - 150)
        self.toolButton.move(new_width - 32, height - 150)
        self.toolButton.resize(32, 32)
        self.toolButton_2.move(new_width - 32, height - 118)
        self.toolButton_2.resize(32, 32)
        
        self.log("Window resized to: " + str(width) + "x" + str(height))
        
    def log(self, text):
        """
        Log text to the textEdit
        """
        self.textEdit.append(text)
        
    def clearLog(self):
        """
        Clear the textEdit
        """
        self.textEdit.clear()
        
    def saveLog(self):
        """
        Save the textEdit to a file
        """
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

if __name__ == "__main__":
    # Create an instance of QtWidgets.QApplication
    app = QtWidgets.QApplication(sys.argv)
    # Show the GUI
    window = AstroPi()
    # Execute the main loop
    sys.exit(app.exec_())