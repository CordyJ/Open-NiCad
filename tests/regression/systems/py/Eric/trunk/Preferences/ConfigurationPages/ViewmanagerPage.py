# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Viewmanager configuration page.
"""

import os

from PyQt4.QtCore import QStringList, pyqtSignature,  QVariant
from PyQt4.QtGui import QPixmap

from KdeQt.KQApplication import e4App

from ConfigurationPageBase import ConfigurationPageBase
from Ui_ViewmanagerPage import Ui_ViewmanagerPage

import Preferences

from eric4config import getConfig

class ViewmanagerPage(ConfigurationPageBase, Ui_ViewmanagerPage):
    """
    Class implementing the Viewmanager configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("ViewmanagerPage")
        
        # set initial values
        self.pluginManager = e4App().getObject("PluginManager")
        self.viewmanagers = self.pluginManager.getPluginDisplayStrings("viewmanager")
        self.windowComboBox.clear()
        currentVm = Preferences.getViewManager()
        
        keys = self.viewmanagers.keys()
        keys.sort()
        for key in keys:
            self.windowComboBox.addItem(self.trUtf8(self.viewmanagers[key]), 
                                        QVariant(key))
        currentIndex = self.windowComboBox.findText(\
            self.trUtf8(self.viewmanagers[currentVm]))
        self.windowComboBox.setCurrentIndex(currentIndex)
        self.on_windowComboBox_activated(currentIndex)
        
        self.tabViewGroupBox.setTitle(self.trUtf8(self.viewmanagers["tabview"]))
        
        self.filenameLengthSpinBox.setValue(
            Preferences.getUI("TabViewManagerFilenameLength"))
        self.filenameOnlyCheckBox.setChecked(
            Preferences.getUI("TabViewManagerFilenameOnly"))
        self.recentFilesSpinBox.setValue(
            Preferences.getUI("RecentNumber"))
        
    def save(self):
        """
        Public slot to save the Viewmanager configuration.
        """
        vm = unicode(\
            self.windowComboBox.itemData(self.windowComboBox.currentIndex()).toString())
        Preferences.setViewManager(vm)
        Preferences.setUI("TabViewManagerFilenameLength",
            self.filenameLengthSpinBox.value())
        Preferences.setUI("TabViewManagerFilenameOnly",
            int(self.filenameOnlyCheckBox.isChecked()))
        Preferences.setUI("RecentNumber", 
            self.recentFilesSpinBox.value())
        
    @pyqtSignature("int")
    def on_windowComboBox_activated(self, index):
        """
        Private slot to show a preview of the selected workspace view type.
        
        @param index index of selected workspace view type (integer)
        """
        workspace = unicode(\
            self.windowComboBox.itemData(self.windowComboBox.currentIndex()).toString())
        pixmap = self.pluginManager.getPluginPreviewPixmap("viewmanager", workspace)
        
        self.previewPixmap.setPixmap(pixmap)
        self.tabViewGroupBox.setEnabled(workspace == "tabview")
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = ViewmanagerPage()
    return page
