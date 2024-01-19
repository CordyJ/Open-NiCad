# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Project configuration page.
"""

from ConfigurationPageBase import ConfigurationPageBase
from Ui_ProjectPage import Ui_ProjectPage

import Preferences

class ProjectPage(ConfigurationPageBase, Ui_ProjectPage):
    """
    Class implementing the Project configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("ProjectPage")
        
        # set initial values
        self.projectCompressedProjectFilesCheckBox.setChecked(\
            Preferences.getProject("CompressedProjectFiles"))
        self.projectSearchNewFilesRecursiveCheckBox.setChecked(\
            Preferences.getProject("SearchNewFilesRecursively"))
        self.projectSearchNewFilesCheckBox.setChecked(\
            Preferences.getProject("SearchNewFiles"))
        self.projectAutoIncludeNewFilesCheckBox.setChecked(\
            Preferences.getProject("AutoIncludeNewFiles"))
        self.projectLoadSessionCheckBox.setChecked(\
            Preferences.getProject("AutoLoadSession"))
        self.projectSaveSessionCheckBox.setChecked(\
            Preferences.getProject("AutoSaveSession"))
        self.projectSessionAllBpCheckBox.setChecked(\
            Preferences.getProject("SessionAllBreakpoints"))
        self.projectLoadDebugPropertiesCheckBox.setChecked(\
            Preferences.getProject("AutoLoadDbgProperties"))
        self.projectSaveDebugPropertiesCheckBox.setChecked(\
            Preferences.getProject("AutoSaveDbgProperties"))
        self.projectAutoCompileFormsCheckBox.setChecked(\
            Preferences.getProject("AutoCompileForms"))
        self.projectAutoCompileResourcesCheckBox.setChecked(\
            Preferences.getProject("AutoCompileResources"))
        self.projectTimestampCheckBox.setChecked(\
            Preferences.getProject("XMLTimestamp"))
        self.projectRecentSpinBox.setValue(
            Preferences.getProject("RecentNumber"))
        
    def save(self):
        """
        Public slot to save the Project configuration.
        """
        Preferences.setProject("CompressedProjectFiles",
            int(self.projectCompressedProjectFilesCheckBox.isChecked()))
        Preferences.setProject("SearchNewFilesRecursively",
            int(self.projectSearchNewFilesRecursiveCheckBox.isChecked()))
        Preferences.setProject("SearchNewFiles",
            int(self.projectSearchNewFilesCheckBox.isChecked()))
        Preferences.setProject("AutoIncludeNewFiles",
            int(self.projectAutoIncludeNewFilesCheckBox.isChecked()))
        Preferences.setProject("AutoLoadSession",
            int(self.projectLoadSessionCheckBox.isChecked()))
        Preferences.setProject("AutoSaveSession",
            int(self.projectSaveSessionCheckBox.isChecked()))
        Preferences.setProject("SessionAllBreakpoints",
            int(self.projectSessionAllBpCheckBox.isChecked()))
        Preferences.setProject("AutoLoadDbgProperties",
            int(self.projectLoadDebugPropertiesCheckBox.isChecked()))
        Preferences.setProject("AutoSaveDbgProperties",
            int(self.projectSaveDebugPropertiesCheckBox.isChecked()))
        Preferences.setProject("AutoCompileForms",
            int(self.projectAutoCompileFormsCheckBox.isChecked()))
        Preferences.setProject("AutoCompileResources",
            int(self.projectAutoCompileResourcesCheckBox.isChecked()))
        Preferences.setProject("XMLTimestamp",
            int(self.projectTimestampCheckBox.isChecked()))
        Preferences.setProject("RecentNumber", 
            self.projectRecentSpinBox.value())
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = ProjectPage()
    return page
