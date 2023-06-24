# Imports
from PyQt5 import QtWidgets, uic, QtGui
from boardcon import BoardCon
import config
import os
class AstroPi(QtWidgets.QMainWindow):
    """
    The main window of the AstroPi application
    """
    def __init__(self):
        """
        Initialize the main window
        """
        super(AstroPi, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'UI/MainWindow.ui'), self) # Load the .ui file
        self.setupUi() # Setup the GUI
        
    def setupUi(self):
        """
        Setup the GUI
        """
        # Log the welcome message
        self.log("""<div style=\'color:turquoise;\'>
 __________________________________________________________________________________________________________________
|<strong>   /$$$$$$              /$$                         /$$$$$$$  /$$ </strong>| <b>AstroPi v0.1-alpha</b>                            |
|<strong>  /$$__  $$            | $$                        | $$__  $$|__/ </strong>| Welcome to AstroPi v0.1-alpha!                |
|<strong> | $$  \ $$  /$$$$$$$ /$$$$$$    /$$$$$$   /$$$$$$ | $$  \ $$ /$$ </strong>| This is a very early version of the software, |
|<strong> | $$$$$$$$ /$$_____/|_  $$_/   /$$__  $$ /$$__  $$| $$$$$$$/| $$ </strong>| so expect bugs and missing features.          |
|<strong> | $$__  $$|  $$$$$$   | $$    | $$  \__/| $$  \ $$| $$____/ | $$ </strong>| If you find any bugs,                         |
|<strong> | $$  | $$ \____  $$  | $$ /$$| $$      | $$  | $$| $$      | $$ </strong>| please report them on GitHub Issues:          |
|<strong> | $$  | $$ /$$$$$$$/  |  $$$$/| $$      |  $$$$$$/| $$      | $$ </strong>| https://github.com/n3rdium/AstroPi/issues     |
|<strong> |__/  |__/|_______/    \___/  |__/       \______/ |__/      |__/ </strong>| <i>CLEAR SKIES!</i>                                  |
|__________________________________________________________________________________________________________________|
</font> """, "log")
        
        # Set the Style Sheets
        self.setStyleSheet("background-color: #222222; color: white;")
        self.Preview.currentWidget().setStyleSheet(f"""background-image: url(\"{os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets/AstroPi.png")}\"); 
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
            self.ConfirmButton,
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
        self.ConfirmButton.clicked.connect(self.enableImagingTab)
        
        # Set default values to text inputs
        self.BoardIP.setText("192.168.0.")
        self.ResolutionX.setText("4056")
        self.ResolutionY.setText("3040")
        self.ImageCount.setText("10")
        self.Interval.setText("0")
        self.ExposureTime.setText("0")
        self.FileTransferPath.setText(os.getcwd())
        self.ISO.setValue(100)
        self.ISOText.setText("ISO [1600]:")
        
        # Set the default values for checkboxes
        self.SaveToDisk.setChecked(False)
        
    def connect(self):
        """
        Attempt to establish a connection to the AstroPi board
        """
        try:
            self.comms = BoardCon(self.BoardIP.text(), self)
            # Now that we have the comms set up, add the button callbacks
            self.SysUpdateButton.clicked.connect(self.comms.updateSystem)
            self.PullUpdatesButton.clicked.connect(self.comms.pullUpdates)
            self.ConnectViaSSHButton.clicked.connect(self.comms.connectViaSSH)
            self.FileTransferPathBrowse.clicked.connect(self.setSaveDir)
            self.SessionAbortButton.clicked.connect(self.comms.abortSession)
            self.StartImagingButton.clicked.connect(self.comms.startImaging)
            # Add the callback for the text input
            self.FileTransferPath.textChanged.connect(self._setSaveDir)
            for ti in self.textEdits[1:-1]:
                ti.editingFinished.connect(self.comms.updateSettings)
            # Add callback for the ISO slider AFTER the slider is left
            self.ISO.sliderReleased.connect(self.updateISO)
        except:
            return
        
    def addImagePreview(self, path):
        """
        Add an image preview to the preview tab
        """
        label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(path)
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        label.setStyleSheet("background-color: black;")
        self.Preview.removeWidget(self.Preview.currentWidget())
        self.Preview.addWidget(label)
    
    def updateISO(self):
        """
        Update the ISO value in the settings
        """
        ISO = int(self.ISO.value() / 100 * 1600)
        if ISO == 1584:
            ISO = 1600
        self.ISOText.setText(f"ISO [{str(ISO)}]:")
        self.comms.config["ISO"] = ISO
        self.comms.updateSettings()
        
    def updateSTD(self):
        """
        Update the save to disk setting in the config
        """
        self.comms.std = self.SaveToDisk.isChecked()

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
        # Callback for the save to disk checkbox
        self.SaveToDisk.stateChanged.connect(self.updateSTD)
        
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
            self.comms.fileSavePath = dir
            self.FileTransferPath.setText(dir)
            self.log("Save directory set to: " + dir, "info")
        
        dialog.close()
        
    def _setSaveDir(self, dir):
        """
        This function is for the text input
        """
        if os.path.isdir(dir):
            self.comms.fileSavePath = dir
            self.log("Save directory set to: " + dir, "info")
        else:
            self.alertPopup("Invalid directory", "The directory you entered is invalid.", "error")
        
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
        try:
            color = config.COLORS[level]
        except:
            color = "white"
        if level == "critical":
            message = "<b>" + message + "</b>"
        self.Console.append("<pre><div style=\'color:" + color + "; margin:0px;\'>" + message + "</div></pre>")
        self.Console.moveCursor(QtGui.QTextCursor.End)
        
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