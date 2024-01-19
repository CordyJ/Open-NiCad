# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to configure the various view profiles.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_ViewProfileDialog import Ui_ViewProfileDialog
from Ui_ViewProfileToolboxesDialog import Ui_ViewProfileToolboxesDialog
from Ui_ViewProfileSidebarsDialog import Ui_ViewProfileSidebarsDialog

class ViewProfileDialog(QDialog):
    """
    Class implementing a dialog to configure the various view profiles.
    """
    def __init__(self, layout, profiles, separateShell, separateBrowser, parent = None):
        """
        Constructor
        
        @param layout type of the window layout (string)
        @param profiles dictionary of tuples containing the visibility
            of the windows for the various profiles
        @param separateShell flag indicating that the Python shell 
            is a separate window
        @param separateBrowser flag indicating that the file browser
            is a separate window
        @param parent parent widget of this dialog (QWidget)
        """
        QDialog.__init__(self, parent)
        
        self.__layout = layout
        if self.__layout == "Toolboxes":
            self.ui = Ui_ViewProfileToolboxesDialog()
        elif self.__layout == "Sidebars":
            self.ui = Ui_ViewProfileSidebarsDialog()
        else:
            self.ui = Ui_ViewProfileDialog()
        self.ui.setupUi(self)
        
        self.profiles = profiles
        
        # set the editor profile
        profile = self.profiles["edit"][0]
        self.ui.epdbCheckBox.setChecked(profile[2])
        if self.__layout in ["Toolboxes", "Sidebars"]:
            profile = self.profiles["edit"][5]
            self.ui.epvtCheckBox.setChecked(profile[0])
            self.ui.ephtCheckBox.setChecked(profile[1])
        else:
            self.ui.eppbCheckBox.setChecked(profile[0])
            if separateBrowser:
                self.ui.epfbCheckBox.setChecked(profile[1])
            else:
                self.ui.epfbCheckBox.setChecked(False)
                self.ui.epfbCheckBox.setEnabled(False)
            if separateShell:
                self.ui.eppsCheckBox.setChecked(profile[3])
            else:
                self.ui.eppsCheckBox.setChecked(False)
                self.ui.eppsCheckBox.setEnabled(False)
            self.ui.eplvCheckBox.setChecked(profile[4])
            self.ui.eptvCheckBox.setChecked(profile[5])
            self.ui.eptevCheckBox.setChecked(profile[6])
            self.ui.epmpbCheckBox.setChecked(profile[7])
            self.ui.eptwCheckBox.setChecked(profile[8])
        
        # set the debug profile
        profile = self.profiles["debug"][0]
        self.ui.dpdbCheckBox.setChecked(profile[2])
        if self.__layout in ["Toolboxes", "Sidebars"]:
            profile = self.profiles["edit"][5]
            self.ui.dpvtCheckBox.setChecked(profile[0])
            self.ui.dphtCheckBox.setChecked(profile[1])
        else:
            self.ui.dppbCheckBox.setChecked(profile[0])
            if separateBrowser:
                self.ui.dpfbCheckBox.setChecked(profile[1])
            else:
                self.ui.dpfbCheckBox.setChecked(False)
                self.ui.dpfbCheckBox.setEnabled(False)
            if separateShell:
                self.ui.dppsCheckBox.setChecked(profile[3])
            else:
                self.ui.dppsCheckBox.setChecked(False)
                self.ui.dppsCheckBox.setEnabled(False)
            self.ui.dplvCheckBox.setChecked(profile[4])
            self.ui.dptvCheckBox.setChecked(profile[5])
            self.ui.dptevCheckBox.setChecked(profile[6])
            self.ui.dpmpbCheckBox.setChecked(profile[7])
            self.ui.dptwCheckBox.setChecked(profile[8])
    
    def getProfiles(self):
        """
        Public method to retrieve the configured profiles.
        
        @return dictionary of tuples containing the visibility
            of the windows for the various profiles
        """
        if self.__layout in ["Toolboxes", "Sidebars"]:
            # get the edit profile
            self.profiles["edit"][0][2] = self.ui.epdbCheckBox.isChecked()
            self.profiles["edit"][5] = [\
                self.ui.epvtCheckBox.isChecked(), 
                self.ui.ephtCheckBox.isChecked(), 
            ]
            # get the debug profile
            self.profiles["debug"][0][2] = self.ui.dpdbCheckBox.isChecked()
            self.profiles["debug"][5] = [\
                self.ui.dpvtCheckBox.isChecked(), 
                self.ui.dphtCheckBox.isChecked(), 
            ]
        else:
            # get the edit profile
            self.profiles["edit"][0] = [\
                self.ui.eppbCheckBox.isChecked(),
                self.ui.epfbCheckBox.isChecked(),
                self.ui.epdbCheckBox.isChecked(),
                self.ui.eppsCheckBox.isChecked(),
                self.ui.eplvCheckBox.isChecked(),
                self.ui.eptvCheckBox.isChecked(),
                self.ui.eptevCheckBox.isChecked(),
                self.ui.epmpbCheckBox.isChecked(),
                self.ui.eptwCheckBox.isChecked(),
            ]
            
            # get the debug profile
            self.profiles["debug"][0] = [\
                self.ui.dppbCheckBox.isChecked(),
                self.ui.dpfbCheckBox.isChecked(),
                self.ui.dpdbCheckBox.isChecked(),
                self.ui.dppsCheckBox.isChecked(),
                self.ui.dplvCheckBox.isChecked(),
                self.ui.dptvCheckBox.isChecked(),
                self.ui.dptevCheckBox.isChecked(),
                self.ui.dpmpbCheckBox.isChecked(),
                self.ui.dptwCheckBox.isChecked(),
            ]
        
        return self.profiles
