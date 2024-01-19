# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor Autocompletion configuration page.
"""

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorAutocompletionPage import Ui_EditorAutocompletionPage

import Preferences

class EditorAutocompletionPage(ConfigurationPageBase, Ui_EditorAutocompletionPage):
    """
    Class implementing the Editor Autocompletion configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorAutocompletionPage")
        
        # set initial values
        self.acEnabledCheckBox.setChecked(\
            Preferences.getEditor("AutoCompletionEnabled"))
        self.acCaseSensitivityCheckBox.setChecked(\
            Preferences.getEditor("AutoCompletionCaseSensitivity"))
        self.acReplaceWordCheckBox.setChecked(\
            Preferences.getEditor("AutoCompletionReplaceWord"))
        self.acThresholdSlider.setValue(\
            Preferences.getEditor("AutoCompletionThreshold"))
        
    def save(self):
        """
        Public slot to save the Editor Autocompletion configuration.
        """
        Preferences.setEditor("AutoCompletionEnabled",
            int(self.acEnabledCheckBox.isChecked()))
        Preferences.setEditor("AutoCompletionCaseSensitivity",
            int(self.acCaseSensitivityCheckBox.isChecked()))
        Preferences.setEditor("AutoCompletionReplaceWord",
            int(self.acReplaceWordCheckBox.isChecked()))
        Preferences.setEditor("AutoCompletionThreshold",
            self.acThresholdSlider.value())
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorAutocompletionPage()
    return page
