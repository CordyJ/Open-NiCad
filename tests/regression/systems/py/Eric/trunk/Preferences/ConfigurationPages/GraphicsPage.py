# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Printer configuration page.
"""

from PyQt4.QtCore import pyqtSignature

from ConfigurationPageBase import ConfigurationPageBase
from Ui_GraphicsPage import Ui_GraphicsPage

import Preferences

class GraphicsPage(ConfigurationPageBase, Ui_GraphicsPage):
    """
    Class implementing the Printer configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("GraphicsPage")
        
        # set initial values
        self.graphicsFont = Preferences.getGraphics("Font")
        self.graphicsFontSample.setFont(self.graphicsFont)
        
    def save(self):
        """
        Public slot to save the Printer configuration.
        """
        Preferences.setGraphics("Font", self.graphicsFont)
        
    @pyqtSignature("")
    def on_graphicsFontButton_clicked(self):
        """
        Private method used to select the font for the graphics items.
        """
        self.graphicsFont = self.selectFont(self.graphicsFontSample, self.graphicsFont)
        
    def polishPage(self):
        """
        Public slot to perform some polishing actions.
        """
        self.graphicsFontSample.setFont(self.graphicsFont)
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = GraphicsPage()
    return page
