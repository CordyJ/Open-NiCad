# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Debugger Ruby configuration page.
"""

from PyQt4.QtCore import QDir, QString, pyqtSignature

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4FileCompleter

from ConfigurationPageBase import ConfigurationPageBase
from Ui_DebuggerRubyPage import Ui_DebuggerRubyPage

import Preferences
import Utilities

class DebuggerRubyPage(ConfigurationPageBase, Ui_DebuggerRubyPage):
    """
    Class implementing the Debugger Ruby configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("DebuggerRubyPage")
        
        self.rubyInterpreterCompleter = E4FileCompleter(self.rubyInterpreterEdit)
        
        # set initial values
        self.rubyInterpreterEdit.setText(\
            Preferences.getDebugger("RubyInterpreter"))
        self.rbRedirectCheckBox.setChecked(\
            Preferences.getDebugger("RubyRedirect"))
        
    def save(self):
        """
        Public slot to save the Debugger Ruby configuration.
        """
        Preferences.setDebugger("RubyInterpreter", 
            self.rubyInterpreterEdit.text())
        Preferences.setDebugger("RubyRedirect", 
            int(self.rbRedirectCheckBox.isChecked()))
        
    @pyqtSignature("")
    def on_rubyInterpreterButton_clicked(self):
        """
        Private slot to handle the Ruby interpreter selection.
        """
        file = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select Ruby interpreter for Debug Client"),
            self.rubyInterpreterEdit.text())
            
        if not file.isEmpty():
            self.rubyInterpreterEdit.setText(\
                Utilities.toNativeSeparators(file))
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = DebuggerRubyPage()
    return page
