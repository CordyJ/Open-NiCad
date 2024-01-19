# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor General configuration page.
"""

from PyQt4.Qsci import QsciScintilla

import QScintilla.Lexers

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorFilePage import Ui_EditorFilePage

from Utilities import supportedCodecs
import Preferences

class EditorFilePage(ConfigurationPageBase, Ui_EditorFilePage):
    """
    Class implementing the Editor File configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorFilePage")
        
        self.openFilesFilterComboBox.addItems(\
            QScintilla.Lexers.getOpenFileFiltersList(True))
        self.saveFilesFilterComboBox.addItems(\
            QScintilla.Lexers.getSaveFileFiltersList(True))
        
        self.defaultEncodingComboBox.addItems(sorted(supportedCodecs))
        
        # set initial values
        self.autosaveSlider.setValue(\
            Preferences.getEditor("AutosaveInterval"))
        self.createBackupFileCheckBox.setChecked(\
            Preferences.getEditor("CreateBackupFile"))
        self.automaticSyntaxCheckCheckBox.setChecked(\
            Preferences.getEditor("AutoCheckSyntax"))
        self.defaultEncodingComboBox.setCurrentIndex(\
            self.defaultEncodingComboBox.findText(\
                Preferences.getEditor("DefaultEncoding")))
        self.advEncodingCheckBox.setChecked(\
            Preferences.getEditor("AdvancedEncodingDetection"))
        self.warnFilesizeSpinBox.setValue(\
            Preferences.getEditor("WarnFilesize"))
        self.clearBreakpointsCheckBox.setChecked(\
            Preferences.getEditor("ClearBreaksOnClose"))
        self.automaticReopenCheckBox.setChecked(\
            Preferences.getEditor("AutoReopen"))
        self.stripWhitespaceCheckBox.setChecked(\
            Preferences.getEditor("StripTrailingWhitespace"))
        self.openFilesFilterComboBox.setCurrentIndex(\
            self.openFilesFilterComboBox.findText(\
                Preferences.getEditor("DefaultOpenFilter")))
        self.saveFilesFilterComboBox.setCurrentIndex(\
            self.saveFilesFilterComboBox.findText(\
                Preferences.getEditor("DefaultSaveFilter")))
        self.automaticEolConversionCheckBox.setChecked(\
            Preferences.getEditor("AutomaticEOLConversion"))
        
        eolMode = Preferences.getEditor("EOLMode")
        if eolMode == QsciScintilla.EolWindows:
            self.crlfRadioButton.setChecked(True)
        elif eolMode == QsciScintilla.EolMac:
            self.crRadioButton.setChecked(True)
        elif eolMode == QsciScintilla.EolUnix:
            self.lfRadioButton.setChecked(True)
        
    def save(self):
        """
        Public slot to save the Editor General configuration.
        """
        Preferences.setEditor("AutosaveInterval", 
            self.autosaveSlider.value())
        Preferences.setEditor("CreateBackupFile",
            int(self.createBackupFileCheckBox.isChecked()))
        Preferences.setEditor("AutoCheckSyntax",
            int(self.automaticSyntaxCheckCheckBox.isChecked()))
        enc = unicode(self.defaultEncodingComboBox.currentText())
        if not enc:
            enc = "utf-8"
        Preferences.setEditor("DefaultEncoding", enc)
        Preferences.setEditor("AdvancedEncodingDetection", 
            int(self.advEncodingCheckBox.isChecked()))
        Preferences.setEditor("WarnFilesize",
            self.warnFilesizeSpinBox.value())
        Preferences.setEditor("ClearBreaksOnClose",
            int(self.clearBreakpointsCheckBox.isChecked()))
        Preferences.setEditor("AutoReopen",
            int(self.automaticReopenCheckBox.isChecked()))
        Preferences.setEditor("StripTrailingWhitespace", 
            int(self.stripWhitespaceCheckBox.isChecked()))
        Preferences.setEditor("DefaultOpenFilter",
            self.openFilesFilterComboBox.currentText())
        Preferences.setEditor("DefaultSaveFilter",
            self.saveFilesFilterComboBox.currentText())
        Preferences.setEditor("AutomaticEOLConversion",
            int(self.automaticEolConversionCheckBox.isChecked()))
        
        if self.crlfRadioButton.isChecked():
            Preferences.setEditor("EOLMode", QsciScintilla.EolWindows)
        elif self.crRadioButton.isChecked():
            Preferences.setEditor("EOLMode", QsciScintilla.EolMac)
        elif self.lfRadioButton.isChecked():
            Preferences.setEditor("EOLMode", QsciScintilla.EolUnix)
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorFilePage()
    return page
