# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Multi Project configuration page.
"""

from ConfigurationPageBase import ConfigurationPageBase
from Ui_MultiProjectPage import Ui_MultiProjectPage

import Preferences

class MultiProjectPage(ConfigurationPageBase, Ui_MultiProjectPage):
    """
    Class implementing the Multi Project configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("MultiProjectPage")
        
        # set initial values
        self.openMasterAutomaticallyCheckBox.setChecked(\
            Preferences.getMultiProject("OpenMasterAutomatically"))
        self.multiProjectTimestampCheckBox.setChecked(\
            Preferences.getMultiProject("XMLTimestamp"))
        self.multiProjectRecentSpinBox.setValue(
            Preferences.getMultiProject("RecentNumber"))
        
    def save(self):
        """
        Public slot to save the Project configuration.
        """
        Preferences.setMultiProject("OpenMasterAutomatically",
            int(self.openMasterAutomaticallyCheckBox.isChecked()))
        Preferences.setMultiProject("XMLTimestamp",
            int(self.multiProjectTimestampCheckBox.isChecked()))
        Preferences.setMultiProject("RecentNumber", 
            self.multiProjectRecentSpinBox.value())
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = MultiProjectPage()
    return page
