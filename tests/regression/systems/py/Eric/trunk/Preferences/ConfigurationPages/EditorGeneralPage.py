# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor General configuration page.
"""

import QScintilla.Lexers

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorGeneralPage import Ui_EditorGeneralPage

import Preferences

class EditorGeneralPage(ConfigurationPageBase, Ui_EditorGeneralPage):
    """
    Class implementing the Editor General configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorGeneralPage")
        
        # set initial values
        self.tabwidthSlider.setValue(\
            Preferences.getEditor("TabWidth"))
        self.indentwidthSlider.setValue(\
            Preferences.getEditor("IndentWidth"))
        self.indentguidesCheckBox.setChecked(\
            Preferences.getEditor("IndentationGuides"))
        self.tabforindentationCheckBox.setChecked(\
            Preferences.getEditor("TabForIndentation"))
        self.tabindentsCheckBox.setChecked(\
            Preferences.getEditor("TabIndents"))
        self.converttabsCheckBox.setChecked(\
            Preferences.getEditor("ConvertTabsOnLoad"))
        self.autoindentCheckBox.setChecked(\
            Preferences.getEditor("AutoIndentation"))
        self.comment0CheckBox.setChecked(
            Preferences.getEditor("CommentColumn0"))
        
    def save(self):
        """
        Public slot to save the Editor General configuration.
        """
        Preferences.setEditor("TabWidth", 
            self.tabwidthSlider.value())
        Preferences.setEditor("IndentWidth", 
            self.indentwidthSlider.value())
        Preferences.setEditor("IndentationGuides",
            int(self.indentguidesCheckBox.isChecked()))
        Preferences.setEditor("TabForIndentation", 
            int(self.tabforindentationCheckBox.isChecked()))
        Preferences.setEditor("TabIndents", 
            int(self.tabindentsCheckBox.isChecked()))
        Preferences.setEditor("ConvertTabsOnLoad",
            int(self.converttabsCheckBox.isChecked()))
        Preferences.setEditor("AutoIndentation", 
            int(self.autoindentCheckBox.isChecked()))
        Preferences.setEditor("CommentColumn0", 
            int(self.comment0CheckBox.isChecked()))
        
    def on_tabforindentationCheckBox_toggled(self, checked):
        """
        Private slot used to set the tab conversion check box.
        
        @param checked flag received from the signal (boolean)
        """
        if checked and self.converttabsCheckBox.isChecked():
            self.converttabsCheckBox.setChecked(not checked)
        self.converttabsCheckBox.setEnabled(not checked)
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorGeneralPage()
    return page
