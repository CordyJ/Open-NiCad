# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Debugger Python configuration page.
"""

from PyQt4.QtCore import QDir, QString, pyqtSignature

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4FileCompleter

from ConfigurationPageBase import ConfigurationPageBase
from Ui_DebuggerPythonPage import Ui_DebuggerPythonPage

import Preferences
import Utilities

class DebuggerPythonPage(ConfigurationPageBase, Ui_DebuggerPythonPage):
    """
    Class implementing the Debugger Python configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("DebuggerPythonPage")
        
        self.interpreterCompleter = E4FileCompleter(self.interpreterEdit)
        self.debugClientCompleter = E4FileCompleter(self.debugClientEdit)
        
        # set initial values
        self.customPyCheckBox.setChecked(\
            Preferences.getDebugger("CustomPythonInterpreter"))
        self.interpreterEdit.setText(\
            Preferences.getDebugger("PythonInterpreter"))
        dct = Preferences.getDebugger("DebugClientType")
        if dct == "standard":
            self.standardButton.setChecked(True)
        elif dct == "threaded":
            self.threadedButton.setChecked(True)
        else:
            self.customButton.setChecked(True)
        self.debugClientEdit.setText(\
            Preferences.getDebugger("DebugClient"))
        self.pyRedirectCheckBox.setChecked(\
            Preferences.getDebugger("PythonRedirect"))
        self.pyNoEncodingCheckBox.setChecked(\
            Preferences.getDebugger("PythonNoEncoding"))
        self.sourceExtensionsEdit.setText(
            Preferences.getDebugger("PythonExtensions"))
        
    def save(self):
        """
        Public slot to save the Debugger Python configuration.
        """
        Preferences.setDebugger("CustomPythonInterpreter", 
            int(self.customPyCheckBox.isChecked()))
        Preferences.setDebugger("PythonInterpreter", 
            self.interpreterEdit.text())
        if self.standardButton.isChecked():
            dct = "standard"
        elif self.threadedButton.isChecked():
            dct = "threaded"
        else:
            dct = "custom"
        Preferences.setDebugger("DebugClientType", dct)
        Preferences.setDebugger("DebugClient", 
            self.debugClientEdit.text())
        Preferences.setDebugger("PythonRedirect", 
            int(self.pyRedirectCheckBox.isChecked()))
        Preferences.setDebugger("PythonNoEncoding", 
            int(self.pyNoEncodingCheckBox.isChecked()))
        Preferences.setDebugger("PythonExtensions", 
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
            self.trUtf8("Python Files (*.py)"))
            
        if not file.isEmpty():
            self.debugClientEdit.setText(\
                Utilities.toNativeSeparators(file))
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = DebuggerPythonPage()
    return page
