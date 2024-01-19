# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Plugin Manager configuration page.
"""

import os

from PyQt4.QtCore import QDir, QString, pyqtSignature
from PyQt4.QtGui import QFileDialog

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4DirCompleter

from ConfigurationPageBase import ConfigurationPageBase
from Ui_PluginManagerPage import Ui_PluginManagerPage

import Preferences
import Utilities

class PluginManagerPage(ConfigurationPageBase, Ui_PluginManagerPage):
    """
    Class implementing the Plugin Manager configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("PluginManagerPage")
        
        self.downloadDirCompleter = E4DirCompleter(self.downloadDirEdit)
        
        # set initial values
        self.activateExternalPluginsCheckBox.setChecked(\
            Preferences.getPluginManager("ActivateExternal"))
        self.downloadDirEdit.setText(\
            Preferences.getPluginManager("DownloadPath"))
        
    def save(self):
        """
        Public slot to save the Viewmanager configuration.
        """
        Preferences.setPluginManager("ActivateExternal", 
            int(self.activateExternalPluginsCheckBox.isChecked()))
        Preferences.setPluginManager("DownloadPath", 
            self.downloadDirEdit.text())
    
    @pyqtSignature("")
    def on_downloadDirButton_clicked(self):
        """
        Private slot to handle the directory selection via dialog.
        """
        directory = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Select plugins download directory"),
            self.downloadDirEdit.text(),
            QFileDialog.Options(QFileDialog.ShowDirsOnly))
            
        if not directory.isNull():
            dn = unicode(Utilities.toNativeSeparators(directory))
            while dn.endswith(os.sep):
                dn = dn[:-1]
            self.downloadDirEdit.setText(dn)
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = PluginManagerPage()
    return page
