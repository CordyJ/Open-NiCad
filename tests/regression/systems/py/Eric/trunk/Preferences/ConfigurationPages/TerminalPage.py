# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Terminal configuration page.
"""

import sys

from PyQt4.QtCore import pyqtSignature

from ConfigurationPageBase import ConfigurationPageBase
from Ui_TerminalPage import Ui_TerminalPage

import Preferences
import Utilities

class TerminalPage(ConfigurationPageBase, Ui_TerminalPage):
    """
    Class implementing the Terminal configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("TerminalPage")
        
        if Utilities.isWindowsPlatform():
            self.shellGroup.setEnabled(False)
        else:
            self.shellCombo.addItems(["ash", "bash", "csh", "ksh", "sh", "tcsh", "zsh"])
        
        # set initial values
        self.linenowidthSlider.setValue(\
            Preferences.getTerminal("LinenoWidth"))
        self.linenoCheckBox.setChecked(\
            Preferences.getTerminal("LinenoMargin"))
        self.syntaxHighlightingCheckBox.setChecked(\
            Preferences.getTerminal("SyntaxHighlightingEnabled"))
        self.historySpinBox.setValue(\
            Preferences.getTerminal("MaxHistoryEntries"))
        
        self.monospacedFont = Preferences.getTerminal("MonospacedFont")
        self.monospacedFontSample.setFont(self.monospacedFont)
        self.monospacedCheckBox.setChecked(\
            Preferences.getTerminal("UseMonospacedFont"))
        self.marginsFont = Preferences.getTerminal("MarginsFont")
        self.marginsFontSample.setFont(self.marginsFont)
        
        self.shellCombo.setEditText(
            Preferences.getTerminal("Shell"))
        self.interactiveCheckBox.setChecked(
            Preferences.getTerminal("ShellInteractive"))
        
    def save(self):
        """
        Public slot to save the Shell configuration.
        """
        Preferences.setTerminal("LinenoWidth",
            self.linenowidthSlider.value())
        Preferences.setTerminal("LinenoMargin",
            int(self.linenoCheckBox.isChecked()))
        Preferences.setTerminal("SyntaxHighlightingEnabled",
            int(self.syntaxHighlightingCheckBox.isChecked()))
        Preferences.setTerminal("MaxHistoryEntries",
            self.historySpinBox.value())
        
        Preferences.setTerminal("MonospacedFont", self.monospacedFont)
        Preferences.setTerminal("UseMonospacedFont",
            int(self.monospacedCheckBox.isChecked()))
        Preferences.setTerminal("MarginsFont", self.marginsFont)
        
        Preferences.setTerminal("Shell", 
            self.shellCombo.currentText())
        Preferences.setTerminal("ShellInteractive", 
            int(self.interactiveCheckBox.isChecked()))
        
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
    page = TerminalPage()
    return page
