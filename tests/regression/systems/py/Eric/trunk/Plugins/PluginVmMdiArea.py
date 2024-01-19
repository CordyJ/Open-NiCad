# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the mdi area view manager plugin.
"""

import os

from PyQt4.QtCore import QT_TRANSLATE_NOOP, QString, qVersion
from PyQt4.QtGui import QPixmap

# Start-Of-Header
name = "Workspace Plugin"
author = "Detlev Offenbach <detlev@die-offenbachs.de>"
autoactivate = False
deactivateable = False
version = "4.4.0"
pluginType = "viewmanager"
pluginTypename = "mdiarea"
displayString = QT_TRANSLATE_NOOP('VmMdiAreaPlugin', 'MDI Area')
className = "VmMdiAreaPlugin"
packageName = "__core__"
shortDescription = "Implements the MDI Area view manager."
longDescription = """This plugin provides the mdi area view manager."""
# End-Of-Header

error = QString("")

def previewPix():
    """
    Module function to return a preview pixmap.
    
    @return preview pixmap (QPixmap)
    """
    fname = os.path.join(os.path.dirname(__file__), 
                         "ViewManagerPlugins", "MdiArea", "preview.png")
    return QPixmap(fname)
    
class VmMdiAreaPlugin(object):
    """
    Class implementing the Workspace view manager plugin.
    """
    def __init__(self, ui):
        """
        Constructor
        
        @param ui reference to the user interface object (UI.UserInterface)
        """
        self.__ui = ui

    def activate(self):
        """
        Public method to activate this plugin.
        
        @return tuple of reference to instantiated viewmanager and 
            activation status (boolean)
        """
        from ViewManagerPlugins.MdiArea.MdiArea import MdiArea
        self.__object = MdiArea(self.__ui)
        return self.__object, True

    def deactivate(self):
        """
        Public method to deactivate this plugin.
        """
        # do nothing for the moment
        pass
