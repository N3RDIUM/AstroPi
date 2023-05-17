# Imports
from PyQt5 import QtWidgets, uic, QtGui
from boardcon import BoardCon
import config

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
        self.log("""<div style=\'color:turquoise;\'>
  /$$$$$$              /$$                         /$$$$$$$  /$$ | AstroPi v0.1-alpha
 /$$__  $$            | $$                        | $$__  $$|__/ | 
| $$  \ $$  /$$$$$$$ /$$$$$$    /$$$$$$   /$$$$$$ | $$  \ $$ /$$ | Welcome to AstroPi v0.1-alpha! 
| $$$$$$$$ /$$_____/|_  $$_/   /$$__  $$ /$$__  $$| $$$$$$$/| $$ | This is a very early version of the software,
| $$__  $$|  $$$$$$   | $$    | $$  \__/| $$  \ $$| $$____/ | $$ | so expect bugs and missing features.
| $$  | $$ \____  $$  | $$ /$$| $$      | $$  | $$| $$      | $$ | If you find any bugs, 
| $$  | $$ /$$$$$$$/  |  $$$$/| $$      |  $$$$$$/| $$      | $$ | please report them on the GitHub page.
|__/  |__/|_______/    \___/  |__/       \______/ |__/      |__/ | CLEAR SKIES!</font>
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
        
        # Reduce paragraph spacing in the log
        self.Console.document().setDocumentMargin(0)
        
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
        
        # Disable all tabs except the first one
        self.Tabs.setTabEnabled(1, False)
        self.Tabs.setTabEnabled(2, False)
        self.Tabs.setTabEnabled(3, False)
        
        # Disable all buttons except the connect button
        for button in self.buttons:
            if button != self.ConnectButton:
                button.setEnabled(False)
                
        # Add button callbacks
        self.ConnectButton.clicked.connect(self.connect)
        
    def connect(self):
        """
        Attempt to establish a connection to the AstroPi board
        """
        try:
            self.comms = BoardCon(self.BoardIP.text(), self)
            self.SysUpdateButton.clicked.connect(self.comms.updateSystem)
            self.PullUpdatesButton.clicked.connect(self.comms.pullUpdates)
            self.ConnectViaSSHButton.clicked.connect(self.comms.connectViaSSH)
        except:
            return

    def enableConfigTabs(self):
        """
        Enable the configuration tabs
        """
        self.Tabs.setTabEnabled(1, True)
        self.Tabs.setTabEnabled(2, True)
        
    def enableImagingTab(self):
        """
        Enable the imaging tab
        """
        self.Tabs.setTabEnabled(3, True)
        
    def retrieveSSHUsername(self):
        """
        Ask the user for SSH username in a popup
        """
        popup = QtWidgets.QInputDialog()
        popup.setAcceptDrops(True)
        popup.setModal(True)
        popup.setWindowTitle("SSH Username")
        popup.setLabelText("Please enter the SSH username for the AstroPi board:")
        popup.setTextValue("pi")
        popup.resize(400, 200)
        popup.exec_()
        return popup.textValue()
        
    def unlockButtons(self):
        """
        Unlock all buttons
        """
        for button in self.buttons:
            button.setEnabled(True)
        
    def log(self, message, level):
        """
        Log a message to the log window
        """
        color = config.COLORS[level]
        if level == "critical":
            message = "<b>" + message + "</b>"
        self.Console.append("<pre><div style=\'color:" + color + "; margin:0px;\'>" + message + "</div></pre>")
        
    def setBoardStatus(self, status):
        self.BoardStatus.setText("Board Status: " + status)
        QtWidgets.QApplication.processEvents()
        
    def alertPopup(self, title, message, type):
        """
        Create an alert popup
        """
        if type == "info":
            QtWidgets.QMessageBox.information(self, title, message)
        elif type == "warning":
            QtWidgets.QMessageBox.warning(self, title, message)
        elif type == "error":
            QtWidgets.QMessageBox.critical(self, title, message)
        else:
            QtWidgets.QMessageBox.information(self, title, message)

# Run the program
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = AstroPi()
    window.show()
    sys.exit(app.exec_())