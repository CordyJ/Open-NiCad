# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Help Viewers configuration page.
"""

from PyQt4.QtCore import QDir, QString, pyqtSignature

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4FileCompleter

from ConfigurationPageBase import ConfigurationPageBase
from Ui_HelpAppearancePage import Ui_HelpAppearancePage

import Preferences
import Utilities

class HelpAppearancePage(ConfigurationPageBase, Ui_HelpAppearancePage):
    """
    Class implementing the Help Viewer Appearance page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("HelpAppearancePage")
        
        self.styleSheetCompleter = E4FileCompleter(self.styleSheetEdit)
        
        self.helpColours = {}
        
        # set initial values
        self.standardFont = Preferences.getHelp("StandardFont")
        self.standardFontSample.setFont(self.standardFont)
        self.standardFontSample.setText(QString("%1 %2")\
            .arg(self.standardFont.family())\
            .arg(self.standardFont.pointSize()))
        
        self.fixedFont = Preferences.getHelp("FixedFont")
        self.fixedFontSample.setFont(self.fixedFont)
        self.fixedFontSample.setText(QString("%1 %2")\
            .arg(self.fixedFont.family())\
            .arg(self.fixedFont.pointSize()))
        
        self.helpColours["SaveUrlColor"] = \
            self.initColour("SaveUrlColor", self.secureURLsColourButton, 
                            Preferences.getHelp)
        
        self.autoLoadImagesCheckBox.setChecked(Preferences.getHelp("AutoLoadImages"))
        
        self.styleSheetEdit.setText(Preferences.getHelp("UserStyleSheet"))
    
    def save(self):
        """
        Public slot to save the Help Viewers configuration.
        """
        Preferences.setHelp("StandardFont", self.standardFont)
        Preferences.setHelp("FixedFont", self.fixedFont)
        
        Preferences.setHelp("AutoLoadImages",
            int(self.autoLoadImagesCheckBox.isChecked()))
        
        Preferences.setHelp("UserStyleSheet", self.styleSheetEdit.text())
        
        for key in self.helpColours.keys():
            Preferences.setHelp(key, self.helpColours[key])
    
    @pyqtSignature("")
    def on_standardFontButton_clicked(self):
        """
        Private method used to select the standard font.
        """
        self.standardFont = \
            self.selectFont(self.standardFontSample, self.standardFont, True)
    
    @pyqtSignature("")
    def on_fixedFontButton_clicked(self):
        """
        Private method used to select the fixed-width font.
        """
        self.fixedFont = \
            self.selectFont(self.fixedFontSample, self.fixedFont, True)
    
    @pyqtSignature("")
    def on_secureURLsColourButton_clicked(self):
        """
        Private slot to set the colour for secure URLs.
        """
        self.helpColours["SaveUrlColor"] = \
            self.selectColour(self.secureURLsColourButton, 
                              self.helpColours["SaveUrlColor"])
    
    @pyqtSignature("")
    def on_styleSheetButton_clicked(self):
        """
        Private slot to handle the user style sheet selection.
        """
        file = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select Style Sheet"),
            self.styleSheetEdit.text(),
            QString())
        
        if not file.isNull():
            self.styleSheetEdit.setText(Utilities.toNativeSeparators(file))
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = HelpAppearancePage()
    return page
