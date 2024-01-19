# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Subversion version control plugin.
"""

import os
import sys

from PyQt4.QtCore import QString, QVariant
from PyQt4.QtGui import QApplication

from KdeQt.KQApplication import e4App

import Preferences
from Preferences.Shortcuts import readShortcuts

from VcsPlugins.vcsSubversion.SvnUtilities import getConfigPath, getServersPath

import Utilities

# Start-Of-Header
name = "Subversion Plugin"
author = "Detlev Offenbach <detlev@die-offenbachs.de>"
autoactivate = False
deactivateable = True
version = "4.4.0"
pluginType = "version_control"
pluginTypename = "Subversion"
className = "VcsSubversionPlugin"
packageName = "__core__"
shortDescription = "Implements the Subversion version control interface."
longDescription = """This plugin provides the Subversion version control interface."""
# End-Of-Header

error = QString("")

def exeDisplayData():
    """
    Public method to support the display of some executable info.
    
    @return dictionary containing the data to query the presence of
        the executable
    """
    exe = 'svn'
    if Utilities.isWindowsPlatform():
        exe += '.exe'
    
    data = {
        "programEntry"      : True, 
        "header"            : QApplication.translate("VcsSubversionPlugin",
                                "Version Control - Subversion (svn)"), 
        "exe"               : exe, 
        "versionCommand"    : '--version', 
        "versionStartsWith" : 'svn', 
        "versionPosition"   : 2, 
        "version"           : "", 
        "versionCleanup"    : None, 
    }
    
    return data

def getVcsSystemIndicator():
    """
    Public function to get the indicators for this version control system.
    
    @return dictionary with indicator as key and a tuple with the vcs name (string)
        and vcs display string (QString)
    """
    global pluginTypename
    data = {}
    exe = 'svn'
    if Utilities.isWindowsPlatform():
        exe += '.exe'
    if Utilities.isinpath(exe):
        data[".svn"] = (pluginTypename, displayString())
        data["_svn"] = (pluginTypename, displayString())
    return data

def displayString():
    """
    Public function to get the display string.
    
    @return display string (QString)
    """
    exe = 'svn'
    if Utilities.isWindowsPlatform():
        exe += '.exe'
    if Utilities.isinpath(exe):
        return QApplication.translate('VcsSubversionPlugin', 'Subversion (svn)')
    else:
        return QString()

subversionCfgPluginObject = None

def createConfigurationPage(configDlg):
    """
    Module function to create the configuration page.
    
    @return reference to the configuration page
    """
    global subversionCfgPluginObject
    from VcsPlugins.vcsSubversion.ConfigurationPage.SubversionPage import SubversionPage
    if subversionCfgPluginObject is None:
        subversionCfgPluginObject = VcsSubversionPlugin(None)
    page = SubversionPage(subversionCfgPluginObject)
    return page
    
def getConfigData():
    """
    Module function returning data as required by the configuration dialog.
    
    @return dictionary with key "zzz_subversionPage" containing the relevant data
    """
    return {
        "zzz_subversionPage" : \
            [QApplication.translate("VcsSubversionPlugin", "Subversion"), 
             os.path.join("VcsPlugins", "vcsSubversion", "icons", 
                          "preferences-subversion.png"),
             createConfigurationPage, "vcsPage", None],
    }
    
def prepareUninstall():
    """
    Module function to prepare for an uninstallation.
    """
    if not e4App().getObject("PluginManager").isPluginLoaded("PluginVcsSubversion"):
        Preferences.Prefs.settings.remove("Subversion")
    
class VcsSubversionPlugin(object):
    """
    Class implementing the Subversion version control plugin.
    """
    def __init__(self, ui):
        """
        Constructor
        
        @param ui reference to the user interface object (UI.UserInterface)
        """
        self.__ui = ui
        
        self.__subversionDefaults = {
            "StopLogOnCopy"  : 1, 
            "LogLimit"       : 100, 
            "CommitMessages" : 20, 
        }
        
        from VcsPlugins.vcsSubversion.ProjectHelper import SvnProjectHelper
        self.__projectHelperObject = SvnProjectHelper(None, None)
        try:
            e4App().registerPluginObject(pluginTypename, self.__projectHelperObject, 
                                         pluginType)
        except KeyError:
            pass    # ignore duplicate registration
        readShortcuts(pluginName = pluginTypename)
    
    def getProjectHelper(self):
        """
        Public method to get a reference to the project helper object.
        
        @return reference to the project helper object
        """
        return self.__projectHelperObject

    def activate(self):
        """
        Public method to activate this plugin.
        
        @return tuple of reference to instantiated viewmanager and 
            activation status (boolean)
        """
        from VcsPlugins.vcsSubversion.subversion import Subversion
        self.__object = Subversion(self, self.__ui)
        return self.__object, True
    
    def deactivate(self):
        """
        Public method to deactivate this plugin.
        """
        self.__object = None
    
    def getPreferences(self, key):
        """
        Public method to retrieve the various refactoring settings.
        
        @param key the key of the value to get
        @param prefClass preferences class used as the storage area
        @return the requested refactoring setting
        """
        if key in ["Commits"]:
            return Preferences.Prefs.settings.value("Subversion/" + key).toStringList()
        else:
            return Preferences.Prefs.settings.value("Subversion/" + key,
                QVariant(self.__subversionDefaults[key])).toInt()[0]
    
    def setPreferences(self, key, value):
        """
        Public method to store the various refactoring settings.
        
        @param key the key of the setting to be set
        @param value the value to be set
        @param prefClass preferences class used as the storage area
        """
        Preferences.Prefs.settings.setValue("Subversion/" + key, QVariant(value))
    
    def getServersPath(self):
        """
        Public method to get the filename of the servers file.
        
        @return filename of the servers file (string)
        """
        return getServersPath()
    
    def getConfigPath(self):
        """
        Public method to get the filename of the config file.
        
        @return filename of the config file (string)
        """
        return getConfigPath()
    
    def prepareUninstall(self):
        """
        Public method to prepare for an uninstallation.
        """
        e4App().unregisterPluginObject(pluginTypename)
