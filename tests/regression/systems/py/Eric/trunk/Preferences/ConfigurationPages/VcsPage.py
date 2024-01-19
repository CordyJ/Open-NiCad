# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the VCS configuration page.
"""

from PyQt4.QtCore import pyqtSignature

from ConfigurationPageBase import ConfigurationPageBase
from Ui_VcsPage import Ui_VcsPage

import Preferences

class VcsPage(ConfigurationPageBase, Ui_VcsPage):
    """
    Class implementing the VCS configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("VcsPage")
        
        self.projectBrowserColours = {}
        
        # set initial values
        self.vcsAutoCloseCheckBox.setChecked(Preferences.getVCS("AutoClose"))
        self.vcsAutoSaveCheckBox.setChecked(Preferences.getVCS("AutoSaveFiles"))
        self.vcsAutoSaveProjectCheckBox.setChecked(
            Preferences.getVCS("AutoSaveProject"))
        self.vcsStatusMonitorIntervalSpinBox.setValue(
            Preferences.getVCS("StatusMonitorInterval"))
        self.vcsMonitorLocalStatusCheckBox.setChecked(
            Preferences.getVCS("MonitorLocalStatus"))
        self.autoUpdateCheckBox.setChecked(
            Preferences.getVCS("AutoUpdate"))
        
        self.projectBrowserColours["VcsAdded"] = \
            self.initColour("VcsAdded", self.pbVcsAddedButton, 
                Preferences.getProjectBrowserColour)
        self.projectBrowserColours["VcsConflict"] = \
            self.initColour("VcsConflict", self.pbVcsConflictButton, 
                Preferences.getProjectBrowserColour)
        self.projectBrowserColours["VcsModified"] = \
            self.initColour("VcsModified", self.pbVcsModifiedButton, 
                Preferences.getProjectBrowserColour)
        self.projectBrowserColours["VcsReplaced"] = \
            self.initColour("VcsReplaced", self.pbVcsReplacedButton, 
                Preferences.getProjectBrowserColour)
        self.projectBrowserColours["VcsUpdate"] = \
            self.initColour("VcsUpdate", self.pbVcsUpdateButton, 
                Preferences.getProjectBrowserColour)
        self.projectBrowserColours["VcsConflict"] = \
            self.initColour("VcsConflict", self.pbVcsConflictButton, 
                Preferences.getProjectBrowserColour)
    
    def save(self):
        """
        Public slot to save the VCS configuration.
        """
        Preferences.setVCS("AutoClose",
            int(self.vcsAutoCloseCheckBox.isChecked()))
        Preferences.setVCS("AutoSaveFiles",
            int(self.vcsAutoSaveCheckBox.isChecked()))
        Preferences.setVCS("AutoSaveProject",
            int(self.vcsAutoSaveProjectCheckBox.isChecked()))
        Preferences.setVCS("StatusMonitorInterval",
            self.vcsStatusMonitorIntervalSpinBox.value())
        Preferences.setVCS("MonitorLocalStatus", 
            int(self.vcsMonitorLocalStatusCheckBox.isChecked()))
        Preferences.setVCS("AutoUpdate", 
            int(self.autoUpdateCheckBox.isChecked()))
    
        for key in self.projectBrowserColours.keys():
            Preferences.setProjectBrowserColour(key, self.projectBrowserColours[key])
    
    @pyqtSignature("")
    def on_pbVcsAddedButton_clicked(self):
        """
        Private slot to set the background colour for entries with VCS 
        status "added".
        """
        self.projectBrowserColours["VcsAdded"] = \
            self.selectColour(self.pbVcsAddedButton, 
                self.projectBrowserColours["VcsAdded"])
        
    @pyqtSignature("")
    def on_pbVcsConflictButton_clicked(self):
        """
        Private slot to set the background colour for entries with VCS 
        status "conflict".
        """
        self.projectBrowserColours["VcsConflict"] = \
            self.selectColour(self.pbVcsConflictButton, 
                self.projectBrowserColours["VcsConflict"])
        
    @pyqtSignature("")
    def on_pbVcsModifiedButton_clicked(self):
        """
        Private slot to set the background colour for entries with VCS 
        status "modified".
        """
        self.projectBrowserColours["VcsModified"] = \
            self.selectColour(self.pbVcsModifiedButton, 
                self.projectBrowserColours["VcsModified"])
        
    @pyqtSignature("")
    def on_pbVcsReplacedButton_clicked(self):
        """
        Private slot to set the background colour for entries with VCS 
        status "replaced".
        """
        self.projectBrowserColours["VcsReplaced"] = \
            self.selectColour(self.pbVcsReplacedButton, 
                self.projectBrowserColours["VcsReplaced"])
        
    @pyqtSignature("")
    def on_pbVcsUpdateButton_clicked(self):
        """
        Private slot to set the background colour for entries with VCS 
        status "needs update".
        """
        self.projectBrowserColours["VcsUpdate"] = \
            self.selectColour(self.pbVcsUpdateButton, 
                self.projectBrowserColours["VcsUpdate"])

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = VcsPage()
    return page
