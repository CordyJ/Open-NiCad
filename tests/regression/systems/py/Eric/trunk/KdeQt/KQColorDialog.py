# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Compatibility module to use the KDE Color Dialog instead of the Qt Color Dialog.
"""

import sys

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QColor

import Preferences

if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
    try:
        from PyKDE4.kdeui import KColorDialog
        
        def __kdeGetColor(initial = Qt.white, parent = None):
            """
            Public function to pop up a modal dialog to select a color.
            
            @param initial initial color to select (QColor)
            @param parent parent widget of the dialog (QWidget)
            @return the selected color or the invalid color, if the user
                canceled the dialog (QColor)
            """
            col = QColor(initial)
            res = KColorDialog.getColor(col, parent)
            if res == KColorDialog.Accepted:
                return col
            else:
                return QColor()
        
    except (ImportError, RuntimeError):
        sys.e4nokde = True
    
from PyQt4.QtGui import QColorDialog

__qtGetColor = QColorDialog.getColor

################################################################################

def getColor(initial = QColor(Qt.white), parent = None):
    """
    Public function to pop up a modal dialog to select a color.
    
    @param initial initial color to select (QColor)
    @param parent parent widget of the dialog (QWidget)
    @return the selected color or the invalid color, if the user
        canceled the dialog (QColor)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeGetColor(initial, parent)
    else:
        return __qtGetColor(initial, parent)
