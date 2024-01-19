# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Compatibility module to use the KDE Print Dialog instead of the Qt Print Dialog.
"""

import sys

import Preferences

if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
    try:
        from PyKDE4.kdeui import KdePrint
        
        def __kdeKQPrintDialog(printer, parent):
            """
            Compatibility function to use the KDE4 print dialog.
            
            @param printer reference to the printer object (QPrinter)
            @param parent reference to the parent widget (QWidget)
            """
            return KdePrint.createPrintDialog(printer, parent)

    except (ImportError, RuntimeError):
        sys.e4nokde = True

from PyQt4.QtGui import QPrintDialog
class __qtKQPrintDialog(QPrintDialog):
    """
    Compatibility class to use the Qt Print Dialog.
    """
    pass

################################################################################

def KQPrintDialog(printer, parent = None):
    """
    Public function to instantiate a printer dialog object.
    
    @param printer reference to the printer object (QPrinter)
    @param parent reference to the parent widget (QWidget)
    @return reference to the printer dialog object
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeKQPrintDialog(printer, parent)
    else:
        return __qtKQPrintDialog(printer, parent)
