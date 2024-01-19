# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Subversion configuration page.
"""

from PyQt4.QtCore import pyqtSignature

from QScintilla.MiniEditor import MiniEditor

from Preferences.ConfigurationPages.ConfigurationPageBase import ConfigurationPageBase
from Ui_SubversionPage import Ui_SubversionPage

class SubversionPage(ConfigurationPageBase, Ui_SubversionPage):
    """
    Class implementing the Subversion configuration page.
    """
    def __init__(self, plugin):
        """
        Constructor
        
        @param plugin reference to the plugin object
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("SubversionPage")
        
        self.__plugin = plugin
        
        # set initial values
        self.logSpinBox.setValue(self.__plugin.getPreferences("LogLimit"))
        self.commitSpinBox.setValue(self.__plugin.getPreferences("CommitMessages"))
        
    def save(self):
        """
        Public slot to save the Subversion configuration.
        """
        self.__plugin.setPreferences("LogLimit", self.logSpinBox.value())
        self.__plugin.setPreferences("CommitMessages", self.commitSpinBox.value())
    
    @pyqtSignature("")
    def on_configButton_clicked(self):
        """
        Private slot to edit the Subversion config file.
        """
        cfgFile = self.__plugin.getConfigPath()
        editor = MiniEditor(cfgFile, "Properties", self)
        editor.show()
    
    @pyqtSignature("")
    def on_serversButton_clicked(self):
        """
        Private slot to edit the Subversion servers file.
        """
        serversFile = self.__plugin.getServersPath()
        editor = MiniEditor(serversFile, "Properties", self)
        editor.show()
