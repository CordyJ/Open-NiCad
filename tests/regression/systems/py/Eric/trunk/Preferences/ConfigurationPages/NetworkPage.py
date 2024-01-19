# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Network configuration page.
"""

import os

from PyQt4.QtCore import QVariant, pyqtSignature
from PyQt4.QtGui import QFileDialog

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4DirCompleter

from ConfigurationPageBase import ConfigurationPageBase
from Ui_NetworkPage import Ui_NetworkPage

import Preferences
import Utilities

class NetworkPage(ConfigurationPageBase, Ui_NetworkPage):
    """
    Class implementing the Network configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("NetworkPage")
        
        self.downloadDirCompleter = E4DirCompleter(self.downloadDirEdit)
        
        self.proxyTypeCombo.addItem(self.trUtf8("Transparent HTTP"), QVariant(0))
        self.proxyTypeCombo.addItem(self.trUtf8("Caching HTTP"), QVariant(1))
        self.proxyTypeCombo.addItem(self.trUtf8("Socks5"), QVariant(2))
        
        # set initial values
        self.downloadDirEdit.setText(Preferences.getUI("DownloadPath"))
        self.requestFilenameCheckBox.setChecked(
            Preferences.getUI("RequestDownloadFilename"))
        
        self.proxyGroup.setChecked(\
            Preferences.getUI("UseProxy"))
        self.proxyTypeCombo.setCurrentIndex(self.proxyTypeCombo.findData(\
            QVariant(Preferences.getUI("ProxyType"))))
        self.proxyHostEdit.setText(\
            Preferences.getUI("ProxyHost"))
        self.proxyUserEdit.setText(\
            Preferences.getUI("ProxyUser"))
        self.proxyPasswordEdit.setText(\
            Preferences.getUI("ProxyPassword"))
        self.proxyPortSpin.setValue(\
            Preferences.getUI("ProxyPort"))
        
    def save(self):
        """
        Public slot to save the Application configuration.
        """
        Preferences.setUI("DownloadPath", 
            self.downloadDirEdit.text())
        Preferences.setUI("RequestDownloadFilename", 
            int(self.requestFilenameCheckBox.isChecked()))
        
        Preferences.setUI("UseProxy",
            int(self.proxyGroup.isChecked()))
        Preferences.setUI("ProxyType", 
            self.proxyTypeCombo.itemData(self.proxyTypeCombo.currentIndex()).toInt()[0])
        Preferences.setUI("ProxyHost",
            self.proxyHostEdit.text())
        Preferences.setUI("ProxyUser",
            self.proxyUserEdit.text())
        Preferences.setUI("ProxyPassword",
            self.proxyPasswordEdit.text())
        Preferences.setUI("ProxyPort",
            self.proxyPortSpin.value())
    
    @pyqtSignature("")
    def on_downloadDirButton_clicked(self):
        """
        Private slot to handle the directory selection via dialog.
        """
        directory = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Select download directory"),
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
    page = NetworkPage()
    return page
