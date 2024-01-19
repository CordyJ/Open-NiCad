# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the QScintilla Calltips configuration page.
"""

from PyQt4.Qsci import QsciScintilla

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorCalltipsQScintillaPage import Ui_EditorCalltipsQScintillaPage

import Preferences

class EditorCalltipsQScintillaPage(ConfigurationPageBase, 
                                   Ui_EditorCalltipsQScintillaPage):
    """
    Class implementing the QScintilla Calltips configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorCalltipsQScintillaPage")
        
        # set initial values
        ctContext = Preferences.getEditor("CallTipsStyle")
        if ctContext == QsciScintilla.CallTipsNoContext:
            self.ctNoContextButton.setChecked(True)
        elif ctContext == QsciScintilla.CallTipsNoAutoCompletionContext:
            self.ctNoAutoCompletionButton.setChecked(True)
        elif ctContext == QsciScintilla.CallTipsContext:
            self.ctContextButton.setChecked(True)
        
    def save(self):
        """
        Public slot to save the EditorCalltips configuration.
        """
        if self.ctNoContextButton.isChecked():
            Preferences.setEditor("CallTipsStyle", 
                                  QsciScintilla.CallTipsNoContext)
        elif self.ctNoAutoCompletionButton.isChecked():
            Preferences.setEditor("CallTipsStyle", 
                                  QsciScintilla.CallTipsNoAutoCompletionContext)
        elif self.ctContextButton.isChecked():
            Preferences.setEditor("CallTipsStyle", 
                                  QsciScintilla.CallTipsContext)

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorCalltipsQScintillaPage()
    return page
