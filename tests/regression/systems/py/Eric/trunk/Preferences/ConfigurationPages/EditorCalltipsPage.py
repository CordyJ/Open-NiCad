# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor Calltips configuration page.
"""

from PyQt4.QtCore import pyqtSignature

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorCalltipsPage import Ui_EditorCalltipsPage

import Preferences

class EditorCalltipsPage(ConfigurationPageBase, Ui_EditorCalltipsPage):
    """
    Class implementing the Editor Calltips configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorCalltipsPage")
        
        # set initial values
        self.ctEnabledCheckBox.setChecked(\
            Preferences.getEditor("CallTipsEnabled"))
        
        self.ctVisibleSlider.setValue(\
            Preferences.getEditor("CallTipsVisible"))
        self.callTipsBackgroundColour = \
            self.initColour("CallTipsBackground", self.calltipsBackgroundButton, 
                Preferences.getEditorColour)
        
        self.ctScintillaCheckBox.setChecked(
            Preferences.getEditor("CallTipsScintillaOnFail"))
        
    def save(self):
        """
        Public slot to save the EditorCalltips configuration.
        """
        Preferences.setEditor("CallTipsEnabled",
            int(self.ctEnabledCheckBox.isChecked()))
        
        Preferences.setEditor("CallTipsVisible",
            self.ctVisibleSlider.value())
        Preferences.setEditorColour("CallTipsBackground", self.callTipsBackgroundColour)
        
        Preferences.setEditor("CallTipsScintillaOnFail", 
            int(self.ctScintillaCheckBox.isChecked()))
        
    @pyqtSignature("")
    def on_calltipsBackgroundButton_clicked(self):
        """
        Private slot to set the background colour for calltips.
        """
        self.callTipsBackgroundColour = \
            self.selectColour(self.calltipsBackgroundButton, 
                self.callTipsBackgroundColour)

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorCalltipsPage()
    return page
