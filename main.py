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
        
    # On resize event
    def resizeEvent(self, event):
        # Get the new size of the window
        size = self.size()
        # Get the current width and height of the window
        width = size.width()
        height = size.height()
        new_width = width - 330
        
        self.label_17.resize(new_width, height - 90)
        self.tabWidget.resize(330, height)
        self.tabWidget.move(new_width, 0)
        self.textEdit.resize(new_width, 90)
        self.textEdit.move(0, height - 150)

if __name__ == "__main__":
    # Create an instance of QtWidgets.QApplication
    app = QtWidgets.QApplication(sys.argv)
    # Show the GUI
    window = AstroPi()
    # Execute the main loop
    sys.exit(app.exec_())