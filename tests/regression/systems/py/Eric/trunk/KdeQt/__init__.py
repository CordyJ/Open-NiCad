# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Package implementing compatibility modules for using KDE dialogs instead og Qt dialogs.

The different modules try to import the KDE dialogs and implement interfaces, that are
compatible with the standard Qt dialog APIs. If the import fails, the modules fall back
to the standard Qt dialogs.

In order for this package to work PyKDE must be installed (see 
<a href="http://www.riverbankcomputing.co.uk/pykde">
http://www.riverbankcomputing.co.uk/pykde</a>.
"""

import sys

import Preferences

if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
    try:
        import PyKDE4
        from PyQt4.QtCore import QString
        
        def __kdeIsKDE():
            """
            Public function to signal the availability of KDE4.
            
            @return availability flag (always True)
            """
            return True
        
    except (ImportError, RuntimeError):
        sys.e4nokde = True

def __kdeKdeVersionString():
    """
    Public function to return the KDE4 version as a string.
    
    @return KDE4 version as a string (QString)
    """
    try:
        try:
            from PyKDE4.kdecore import versionMajor, versionMinor, versionRelease
            return QString("%d.%d.%d" % \
                (versionMajor(), versionMinor(), versionRelease()))
        except (ImportError, AttributeError):
            from PyKDE4 import pykdeconfig
            try:
                return QString(pykdeconfig.Configuration().kde_version_str)
            except AttributeError:
                return QString("unknown")
    except ImportError:
        return QString("unknown")
    
def __kdePyKdeVersionString():
    """
    Public function to return the PyKDE4 version as a string.
    
    @return PyKDE4 version as a string (QString)
    """
    try:
        try:
            from PyKDE4.kdecore import pykde_versionMajor, pykde_versionMinor, \
                                       pykde_versionRelease
            return QString("%d.%d.%d" % \
                (pykde_versionMajor(), pykde_versionMinor(), 
                 pykde_versionRelease()))
        except (ImportError, AttributeError):
            from PyKDE4 import pykdeconfig
            try:
                return QString(pykdeconfig.Configuration().pykde_version_str)
            except AttributeError:
                return QString("unknown")
    except ImportError:
        return QString("unknown")
    
from PyQt4.QtCore import QString

def __qtIsKDE():
    """
    Private function to signal the availability of KDE.
    
    @return availability flag (always False)
    """
    return False
    
def __qtKdeVersionString():
    """
    Private function to return the KDE version as a string.
    
    @return KDE version as a string (QString) (always empty)
    """
    return QString("")
    
def __qtPyKdeVersionString():
    """
    Private function to return the PyKDE version as a string.
    
    @return PyKDE version as a string (QString) (always empty)
    """
    return QString("")

################################################################################

def isKDEAvailable():
    """
    Public function to signal the availability of KDE.
    
    @return availability flag (always False)
    """
    try:
        import PyKDE4
        return True
    except ImportError:
        return False

def isKDE():
    """
    Public function to signal, if KDE usage is enabled.
    
    @return KDE support flag (always False)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeIsKDE()
    else:
        return __qtIsKDE()
    
def kdeVersionString():
    """
    Public function to return the KDE version as a string.
    
    @return KDE version as a string (QString) (always empty)
    """
    if isKDEAvailable():
        return __kdeKdeVersionString()
    else:
        return __qtKdeVersionString()
    
def pyKdeVersionString():
    """
    Public function to return the PyKDE version as a string.
    
    @return PyKDE version as a string (QString) (always empty)
    """
    if isKDEAvailable():
        return __kdePyKdeVersionString()
    else:
        return __qtPyKdeVersionString()
