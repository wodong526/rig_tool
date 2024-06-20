"""
This Module:
- Handles the design part of UI  
"""
# import sys
# sys.path.append("..") # Adds higher directory to python modules path.

#from LiveLink import MAYA_PLUGIN_VERSION
from Megascans.ImporterSetup import importerSetup
import os



try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2.QtWidgets import QWidget
except:
    try:
        from PySide.QtGui import *
        from PySide.QtCore import *
    except:
        try:
            from PyQt5.QtGui import *
            from PyQ5.QtCore import *
            from PyQ5.QtWidgets import *
        except:
            try:
                from PyQt4.QtGui import *
                from PyQ4.QtCore import *
            except:
                pass


""" GetHostApp returns the host application window as a parent for our widget """
def GetHostApp():
    try:
        mainWindow = QApplication.activeWindow()
        while True:
            lastWin = mainWindow.parent()
            if lastWin:
                mainWindow = lastWin
            else:
                break
        return mainWindow
    except:
        pass



"""
#################################################################################################
#################################################################################################
"""

stylesheet_ = ("""

QCheckBox { background: transparent; color: #E6E6E6; font-family: Source Sans Pro; font-size: 14px; }
QCheckBox::indicator:hover { border: 2px solid #2B98F0; background-color: transparent; }
QCheckBox::indicator:checked:hover { background-color: #2B98F0; border: 2px solid #73a5ce; }
QCheckBox:indicator{ color: #67696a; background-color: transparent; border: 2px solid #67696a;
width: 14px; height: 14px; border-radius: 2px; }
QCheckBox::indicator:checked { border: 2px solid #18191b;
background-color: #2B98F0; color: #ffffff; }
QCheckBox::hover { spacing: 12px; background: transparent; color: #ffffff; }
QCheckBox::checked { color: #ffffff; }
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled { border: 1px solid #444; }
QCheckBox:disabled { background: transparent; color: #414141; font-family: Source Sans Pro;
font-size: 14px; margin: 0px; text-align: center; }

QComboBox { color: #FFFFFF; font-size: 14px; padding: 2px 2px 2px 8px; font-family: Source Sans Pro;
selection-background-color: #1d1e1f; background-color: #1d1e1f; }
QComboBox:hover { color: #c9c9c9; font-size: 14px; padding: 2px 2px 2px 8px; font-family: Source Sans Pro;
selection-background-color: #232426; background-color: #232426; } """)


"""
#################################################################################################
#################################################################################################
"""

# Create the UI widget opened when LiveLink button is clicked
class LiveLinkUI(QWidget):

    Instance = []
    Settings = [0, 0, 0]

    def __init__(self, _importerSetup_, MAYA_PLUGIN_VERSION):
        super(LiveLinkUI, self).__init__()


        LiveLinkUI.Instance = self
        self.Importer = _importerSetup_
        self.Importer.loadApplyToSelection()

        self._path_ = os.path.dirname(__file__).replace("\\", "/")

        self.setObjectName("LiveLinkUI")
        img_ = QPixmap( os.path.join(self._path_, "MS_Logo.png") )
        self.setWindowIcon(QIcon(img_))
        self.setMinimumWidth(275)
        self.setWindowTitle("MS Plugin " + MAYA_PLUGIN_VERSION + " - Maya")
        self.setWindowFlags(Qt.Window)

        self.style_ = ("""  QWidget#LiveLinkUI { background-color: #262729; } """)
        self.setStyleSheet(self.style_)

        # Set the main layout
        self.MainLayout = QVBoxLayout()
        self.setLayout(self.MainLayout)
        self.MainLayout.setSpacing(5)
        self.MainLayout.setContentsMargins(5, 2, 5, 2)


        #Set the checkbox options

        self.checks_l = QVBoxLayout()
        self.checks_l.setSpacing(2)
        self.MainLayout.addLayout(self.checks_l)

        self.applytoSel = QCheckBox("Apply Material to Selection")
        self.applytoSel.setToolTip("Applies the imported material(s) to your selection\?n prior to the import.")
        self.applytoSel.setChecked( self.Importer.getApplyToSelection())
        self.applytoSel.setFixedHeight(30)
        self.applytoSel.setStyleSheet(stylesheet_)

        self.checks_l.addWidget(self.applytoSel)

        self.applytoSel.stateChanged.connect(self.settingsChanged)


    # Check if there were any changes made in UI settings
    def settingsChanged(self):
        self.Importer.updateApplyToSelection(self.applytoSel.isChecked())
        

# Setup the UI of LiveLink
def initUI(MAYA_PLUGIN_VERSION,openUI = True):
    #_importerSetup_ = importerSetup()
    # if LiveLinkUI.Instance != None:
    #     try: 
    #         LiveLinkUI.Instance.close()
    #     except:
    #          pass

    LiveLinkUI.Instance = LiveLinkUI(importerSetup.getInstance(),MAYA_PLUGIN_VERSION)
    LiveLinkUI.Instance.show()
    pref_geo = QRect(500, 300, 460, 30)
    LiveLinkUI.Instance.setGeometry(pref_geo)
    #return LiveLinkUI.Instance
