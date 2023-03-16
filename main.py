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
        self.scrollArea_4.resize(new_width, 90)
        self.scrollArea_4.move(0, height - 140)
        self.scrollArea.resize(new_width, height - 128)
        self.scrollArea_2.resize(new_width, height - 128)
        self.scrollArea_3.resize(new_width, height - 128)
        self.label_4.move(self.label_4.x(), height - 10)
        self.label_14.move(self.label_14.y(), height - 10)
        self.label_16.move(self.label_16.x(), height - 10)

if __name__ == "__main__":
    # Create an instance of QtWidgets.QApplication
    app = QtWidgets.QApplication(sys.argv)
    # Show the GUI
    window = AstroPi()
    # Execute the main loop
    sys.exit(app.exec_())