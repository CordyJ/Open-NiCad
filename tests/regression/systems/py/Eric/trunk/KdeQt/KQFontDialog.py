# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Compatibility module to use the KDE Font Dialog instead of the Qt Font Dialog.
"""

import sys

import Preferences

if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
    try:
        from PyKDE4.kdeui import KFontDialog, KFontChooser
        from PyQt4.QtGui import QFont
        
        def __kdeGetFont(initial, parent = None):
            """
            Public function to pop up a modal dialog to select a font.
            
            @param initial initial font to select (QFont)
            @param parent parent widget of the dialog (QWidget)
            @return the selected font or the initial font, if the user
                canceled the dialog (QFont) and a flag indicating
                the user selection of the OK button (boolean)
            """
            font = QFont(initial)
            res = KFontDialog.getFont(font, 
                                      KFontChooser.DisplayFlags(KFontChooser.NoDisplayFlags),
                                      parent)[0]
            if res == KFontDialog.Accepted:
                return font, True
            else:
                return initial, False
        
    except (ImportError, RuntimeError):
        sys.e4nokde = True

import PyQt4.QtGui
__qtGetFont = PyQt4.QtGui.QFontDialog.getFont

################################################################################

def getFont(initial, parent = None):
    """
    Public function to pop up a modal dialog to select a font.
    
    @param initial initial font to select (QFont)
    @param parent parent widget of the dialog (QWidget)
    @return the selected font or the initial font, if the user
        canceled the dialog (QFont) and a flag indicating
        the user selection of the OK button (boolean)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeGetFont(initial, parent)
    else:
        return __qtGetFont(initial, parent)
