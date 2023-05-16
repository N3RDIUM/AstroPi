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
        # Log the welcome message
        self.log("""<pre><font color="turquoise">
  /$$$$$$              /$$                         /$$$$$$$  /$$ | AstroPi v0.1-alpha
 /$$__  $$            | $$                        | $$__  $$|__/ | 
| $$  \ $$  /$$$$$$$ /$$$$$$    /$$$$$$   /$$$$$$ | $$  \ $$ /$$ | Welcome to AstroPi v0.1-alpha! 
| $$$$$$$$ /$$_____/|_  $$_/   /$$__  $$ /$$__  $$| $$$$$$$/| $$ | This is a very early version of the software,
| $$__  $$|  $$$$$$   | $$    | $$  \__/| $$  \ $$| $$____/ | $$ | so expect bugs and missing features.
| $$  | $$ \____  $$  | $$ /$$| $$      | $$  | $$| $$      | $$ | If you find any bugs, 
| $$  | $$ /$$$$$$$/  |  $$$$/| $$      |  $$$$$$/| $$      | $$ | please report them on the GitHub page.
|__/  |__/|_______/    \___/  |__/       \______/ |__/      |__/ | CLEAR SKIES!</font></pre>
""", "log")
        
        # Set the Style Sheets
        self.setStyleSheet("background-color: #222222; color: white;")
        self.Preview.currentWidget().setStyleSheet("""background-image: url(\"./assets/AstroPi.png\"); 
                                    background-repeat: no-repeat; 
                                    background-position: center; 
                                    background-color: black;""")
        self.ISO.setStyleSheet("color: #006087;")
        self.SettingsReview.setStyleSheet("background-color: #001d87; color: white;")
        self.Console.setStyleSheet("background-color: #303547; color: white;")
        
        self.textEdits = [
            self.BoardIP, 
            self.ResolutionX, 
            self.ResolutionY, 
            self.ImageCount, 
            self.Interval, 
            self.ExposureTime,
            self.FileTransferPath,
        ]
        for textEdit in self.textEdits:
            textEdit.setStyleSheet("background-color: #006087; color: white;")
            
        self.buttons = [
            self.ConnectButton,
            self.SysUpdateButton,
            self.PullUpdatesButton,
            self.ConnectViaSSHButton,
            self.FileTransferPathBrowse,
            self.SessionAbortButton,
            self.StartImagingButton,
        ]
        for button in self.buttons:
            button.setStyleSheet("background-color: #260087; color: white;")
            
        # Set the window title and icon
        self.setWindowTitle("AstroPi")
        self.setWindowIcon(QtGui.QIcon('./assets/AstroPi.ico'))
        
        # Add text edit callbacks
        for textEdit in self.textEdits:
            textEdit.editingFinished.connect(self.textEditCallback)
        
        # Add button callbacks
        for button in self.buttons:
            button.clicked.connect(self.buttonCallback)
            
        # Add callbacks for the slider
        self.ISO.valueChanged.connect(self.ISOCallback)
        
        # Disable all tabs except the first one
        self.Tabs.setTabEnabled(1, False)
        self.Tabs.setTabEnabled(2, False)
        self.Tabs.setTabEnabled(3, False)
        
    def textEditCallback(self, event):
        pass
    def buttonCallback(self, event):
        pass
    def ISOCallback(self, event):
        pass
        
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