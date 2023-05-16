# Imports
from PyQt5 import QtWidgets, uic, QtGui, QtCore

# Constants
COLORS = {
    "log": "white",
    "info": "blue",
    "warning": "yellow",
    "error": "red",
    "critical": "red"
}

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
        self.setupUi() # Setup the GUI
        
    def setupUi(self):
        """
        Setup the GUI
        """
        # Set the Style Sheets
        self.setStyleSheet("background-color: #222222; color: white;")
        
        self.Preview.currentWidget().setStyleSheet("""background-image: url(\"./assets/AstroPi.png\"); 
                                    background-repeat: no-repeat; 
                                    background-position: center; 
                                    background-color: black;""")
        
        self.log("""<pre><font color="turquoise">
  /$$$$$$              /$$                         /$$$$$$$  /$$
 /$$__  $$            | $$                        | $$__  $$|__/
| $$  \ $$  /$$$$$$$ /$$$$$$    /$$$$$$   /$$$$$$ | $$  \ $$ /$$
| $$$$$$$$ /$$_____/|_  $$_/   /$$__  $$ /$$__  $$| $$$$$$$/| $$
| $$__  $$|  $$$$$$   | $$    | $$  \__/| $$  \ $$| $$____/ | $$
| $$  | $$ \____  $$  | $$ /$$| $$      | $$  | $$| $$      | $$
| $$  | $$ /$$$$$$$/  |  $$$$/| $$      |  $$$$$$/| $$      | $$
|__/  |__/|_______/    \___/  |__/       \______/ |__/      |__/</font></pre><br>
<h2><font color="turquoise">AstroPi v0.1-alpha</font></h2><br>
Welcome to AstroPi v0.1-alpha! This is a very early version of the software, so expect bugs and missing features.""", "log")
        
        self.textEdits = [
            self.BoardIP, 
            self.ResolutionX, 
            self.ResolutionY, 
            self.ImageCount, 
            self.Interval, 
            self.ExposureTime
        ]
        for textEdit in self.textEdits:
            textEdit.setStyleSheet("background-color: #333333; color: white;")
        
        self.SettingsReview.setStyleSheet("background-color: #333333; color: white;")
        
        
        
    def log(self, message, level):
        """
        Log a message to the log window
        """
        color = COLORS[level]
        if level == "critical":
            message = "<b>" + message + "</b>"
        self.Console.append("<font color='" + color + "'>" + message + "</font>&nbsp;")
        
# Run the program
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = AstroPi()
    window.show()
    sys.exit(app.exec_())