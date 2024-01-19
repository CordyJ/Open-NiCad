# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Shell configuration page.
"""

from PyQt4.QtCore import pyqtSignature

from ConfigurationPageBase import ConfigurationPageBase
from Ui_ShellPage import Ui_ShellPage

import Preferences

class ShellPage(ConfigurationPageBase, Ui_ShellPage):
    """
    Class implementing the Shell configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("ShellPage")
        
        # set initial values
        self.shellLinenowidthSlider.setValue(
            Preferences.getShell("LinenoWidth"))
        self.shellLinenoCheckBox.setChecked(
            Preferences.getShell("LinenoMargin"))
        self.shellWordWrapCheckBox.setChecked(
            Preferences.getShell("WrapEnabled"))
        self.shellACEnabledCheckBox.setChecked(
            Preferences.getShell("AutoCompletionEnabled"))
        self.shellCTEnabledCheckBox.setChecked(
            Preferences.getShell("CallTipsEnabled"))
        self.shellSyntaxHighlightingCheckBox.setChecked(
            Preferences.getShell("SyntaxHighlightingEnabled"))
        self.shellHistorySpinBox.setValue(
            Preferences.getShell("MaxHistoryEntries"))
        self.stdOutErrCheckBox.setChecked(
            Preferences.getShell("ShowStdOutErr"))
        
        self.monospacedFont = Preferences.getShell("MonospacedFont")
        self.monospacedFontSample.setFont(self.monospacedFont)
        self.monospacedCheckBox.setChecked(\
            Preferences.getShell("UseMonospacedFont"))
        self.marginsFont = Preferences.getShell("MarginsFont")
        self.marginsFontSample.setFont(self.marginsFont)
        
    def save(self):
        """
        Public slot to save the Shell configuration.
        """
        Preferences.setShell("LinenoWidth",
            self.shellLinenowidthSlider.value())
        Preferences.setShell("LinenoMargin",
            int(self.shellLinenoCheckBox.isChecked()))
        Preferences.setShell("WrapEnabled",
            int(self.shellWordWrapCheckBox.isChecked()))
        Preferences.setShell("AutoCompletionEnabled",
            int(self.shellACEnabledCheckBox.isChecked()))
        Preferences.setShell("CallTipsEnabled",
            int(self.shellCTEnabledCheckBox.isChecked()))
        Preferences.setShell("SyntaxHighlightingEnabled",
            int(self.shellSyntaxHighlightingCheckBox.isChecked()))
        Preferences.setShell("MaxHistoryEntries",
            self.shellHistorySpinBox.value())
        Preferences.setShell("ShowStdOutErr", 
            int(self.stdOutErrCheckBox.isChecked()))
        
        Preferences.setShell("MonospacedFont", self.monospacedFont)
        Preferences.setShell("UseMonospacedFont",
            int(self.monospacedCheckBox.isChecked()))
        Preferences.setShell("MarginsFont", self.marginsFont)
        
    @pyqtSignature("")
    def on_monospacedFontButton_clicked(self):
        """
        Private method used to select the font to be used as the monospaced font.
        """
        self.monospacedFont = \
            self.selectFont(self.monospacedFontSample, self.monospacedFont)
        
    @pyqtSignature("")
    def on_linenumbersFontButton_clicked(self):
        """
        Private method used to select the font for the editor margins.
        """
        self.marginsFont = self.selectFont(self.marginsFontSample, self.marginsFont)
        
    def polishPage(self):
        """
        Public slot to perform some polishing actions.
        """
        self.monospacedFontSample.setFont(self.monospacedFont)
        self.marginsFontSample.setFont(self.marginsFont)
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = ShellPage()
    return page
