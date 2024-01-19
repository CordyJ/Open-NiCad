# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor Search configuration page.
"""

from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QPixmap, QIcon

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorSearchPage import Ui_EditorSearchPage

import Preferences

class EditorSearchPage(ConfigurationPageBase, Ui_EditorSearchPage):
    """
    Class implementing the Editor Search configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorSearchPage")
        
        self.editorColours = {}
        
        # set initial values
        self.searchMarkersEnabledCheckBox.setChecked(\
            Preferences.getEditor("SearchMarkersEnabled"))
        self.quicksearchMarkersEnabledCheckBox.setChecked(\
            Preferences.getEditor("QuickSearchMarkersEnabled"))
        self.occurrencesMarkersEnabledCheckBox.setChecked(\
            Preferences.getEditor("MarkOccurrencesEnabled"))
        
        self.markOccurrencesTimeoutSpinBox.setValue(
            Preferences.getEditor("MarkOccurrencesTimeout"))
        
        self.editorColours["SearchMarkers"] = \
            self.initColour("SearchMarkers", self.searchMarkerButton, 
                Preferences.getEditorColour)
        
    def save(self):
        """
        Public slot to save the Editor Search configuration.
        """
        Preferences.setEditor("SearchMarkersEnabled", 
            int(self.searchMarkersEnabledCheckBox.isChecked()))
        Preferences.setEditor("QuickSearchMarkersEnabled", 
            int(self.quicksearchMarkersEnabledCheckBox.isChecked()))
        Preferences.setEditor("MarkOccurrencesEnabled", 
            int(self.occurrencesMarkersEnabledCheckBox.isChecked()))
        
        Preferences.setEditor("MarkOccurrencesTimeout", 
            self.markOccurrencesTimeoutSpinBox.value())
        
        for key in self.editorColours.keys():
            Preferences.setEditorColour(key, self.editorColours[key])
        
    @pyqtSignature("")
    def on_searchMarkerButton_clicked(self):
        """
        Private slot to set the colour of the search markers.
        """
        self.editorColours["SearchMarkers"] = \
            self.selectColour(self.searchMarkerButton, 
                self.editorColours["SearchMarkers"])

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorSearchPage()
    return page
