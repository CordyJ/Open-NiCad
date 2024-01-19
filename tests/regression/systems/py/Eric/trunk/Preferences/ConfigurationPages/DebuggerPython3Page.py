# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Debugger Python3 configuration page.
"""

from PyQt4.QtCore import QDir, QString, pyqtSignature

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4FileCompleter

from ConfigurationPageBase import ConfigurationPageBase
from Ui_DebuggerPython3Page import Ui_DebuggerPython3Page

import Preferences
import Utilities

class DebuggerPython3Page(ConfigurationPageBase, Ui_DebuggerPython3Page):
    """
    Class implementing the Debugger Python3 configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("DebuggerPython3Page")
        
        self.interpreterCompleter = E4FileCompleter(self.interpreterEdit)
        self.debugClientCompleter = E4FileCompleter(self.debugClientEdit)
        
        # set initial values
        self.interpreterEdit.setText(\
            Preferences.getDebugger("Python3Interpreter"))
        dct = Preferences.getDebugger("DebugClientType3")
        if dct == "standard":
            self.standardButton.setChecked(True)
        elif dct == "threaded":
            self.threadedButton.setChecked(True)
        else:
            self.customButton.setChecked(True)
        self.debugClientEdit.setText(
            Preferences.getDebugger("DebugClient3"))
        self.pyRedirectCheckBox.setChecked(
            Preferences.getDebugger("Python3Redirect"))
        self.pyNoEncodingCheckBox.setChecked(
            Preferences.getDebugger("Python3NoEncoding"))
        self.sourceExtensionsEdit.setText(
            Preferences.getDebugger("Python3Extensions"))
        
    def save(self):
        """
        Public slot to save the Debugger Python configuration.
        """
        Preferences.setDebugger("Python3Interpreter", 
            self.interpreterEdit.text())
        if self.standardButton.isChecked():
            dct = "standard"
        elif self.threadedButton.isChecked():
            dct = "threaded"
        else:
            dct = "custom"
        Preferences.setDebugger("DebugClientType3", dct)
        Preferences.setDebugger("DebugClient3", 
            self.debugClientEdit.text())
        Preferences.setDebugger("Python3Redirect", 
            int(self.pyRedirectCheckBox.isChecked()))
        Preferences.setDebugger("Python3NoEncoding", 
            int(self.pyNoEncodingCheckBox.isChecked()))
        Preferences.setDebugger("Python3Extensions", 
            self.sourceExtensionsEdit.text())
        
    @pyqtSignature("")
    def on_interpreterButton_clicked(self):
        """
        Private slot to handle the Python interpreter selection.
        """
        file = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select Python interpreter for Debug Client"),
            self.interpreterEdit.text(),
            QString())
            
        if not file.isEmpty():
            self.interpreterEdit.setText(\
                Utilities.toNativeSeparators(file))
        
    @pyqtSignature("")
    def on_debugClientButton_clicked(self):
        """
        Private slot to handle the Debug Client selection.
        """
        file = KQFileDialog.getOpenFileName(\
            None,
            self.trUtf8("Select Debug Client"),
            self.debugClientEdit.text(),
            self.trUtf8("Python Files (*.py *.py3)"))
            
        if not file.isEmpty():
            self.debugClientEdit.setText(\
                Utilities.toNativeSeparators(file))
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = DebuggerPython3Page()
    return page
