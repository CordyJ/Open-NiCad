# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Templates configuration page.
"""

from ConfigurationPageBase import ConfigurationPageBase
from Ui_TemplatesPage import Ui_TemplatesPage

import Preferences

class TemplatesPage(ConfigurationPageBase, Ui_TemplatesPage):
    """
    Class implementing the Templates configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("TemplatesPage")
        
        # set initial values
        self.templatesAutoOpenGroupsCheckBox.setChecked(\
            Preferences.getTemplates("AutoOpenGroups"))
        self.templatesSeparatorCharEdit.setText(\
            Preferences.getTemplates("SeparatorChar"))
        if Preferences.getTemplates("SingleDialog"):
            self.templatesSingleDialogButton.setChecked(True)
        else:
            self.templatesMultiDialogButton.setChecked(True)
        self.templatesToolTipCheckBox.setChecked(\
            Preferences.getTemplates("ShowTooltip"))
        
    def save(self):
        """
        Public slot to save the Templates configuration.
        """
        Preferences.setTemplates("AutoOpenGroups",
            int(self.templatesAutoOpenGroupsCheckBox.isChecked()))
        sepChar = self.templatesSeparatorCharEdit.text()
        if not sepChar.isEmpty():
            Preferences.setTemplates("SeparatorChar", unicode(sepChar))
        Preferences.setTemplates("SingleDialog",
            int(self.templatesSingleDialogButton.isChecked()))
        Preferences.setTemplates("ShowTooltip",
            int(self.templatesToolTipCheckBox.isChecked()))
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = TemplatesPage()
    return page
