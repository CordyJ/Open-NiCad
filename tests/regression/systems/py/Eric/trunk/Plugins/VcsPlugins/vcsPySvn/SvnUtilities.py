# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing some common utility functions for the pysvn package.
"""

import sys
import os

from PyQt4.QtCore import QDateTime, Qt

import Utilities

def formatTime(seconds):
    """
    Module function to return a formatted time string.
    
    @param seconds time in seconds since epoch to be formatted (float or long)
    @return formatted time string (QString)
    """
    return QDateTime.fromTime_t(long(seconds))\
                    .toTimeSpec(Qt.LocalTime)\
                    .toString("yyyy-MM-dd hh:mm:ss")

def dateFromTime_t(seconds):
    """
    Module function to return the date.
    
    @param seconds time in seconds since epoch to be formatted (float or long)
    @return date (QDate)
    """
    return QDateTime.fromTime_t(long(seconds)).toTimeSpec(Qt.LocalTime).date()

def getServersPath():
    """
    Public method to get the filename of the servers file.
    
    @return filename of the servers file (string)
    """
    if Utilities.isWindowsPlatform():
        appdata = os.environ["APPDATA"]
        return os.path.join(appdata, "Subversion", "servers")
    else:
        homedir = Utilities.getHomeDir()
        return os.path.join(homedir, ".subversion", "servers")

def getConfigPath():
    """
    Public method to get the filename of the config file.
    
    @return filename of the config file (string)
    """
    if Utilities.isWindowsPlatform():
        appdata = os.environ["APPDATA"]
        return os.path.join(appdata, "Subversion", "config")
    else:
        homedir = Utilities.getHomeDir()
        return os.path.join(homedir, ".subversion", "config")