# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Compatibility module to use the KDE Printer instead of the Qt Printer.
"""

import sys

from PyQt4.QtGui import QPrinter

import Preferences

class __kdeKQPrinter(QPrinter):
    """
    Compatibility class to use the Qt Printer.
    """
    pass

class __qtKQPrinter(QPrinter):
    """
    Compatibility class to use the Qt Printer.
    """
    pass

################################################################################

def KQPrinter(mode = QPrinter.ScreenResolution):
    """
    Public function to instantiate a printer object.
    
    @param mode printer mode (QPrinter.PrinterMode)
    @return reference to the printer object
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeKQPrinter(mode)
    else:
        return __qtKQPrinter(mode)

Color = QPrinter.Color
GrayScale = QPrinter.GrayScale

FirstPageFirst = QPrinter.FirstPageFirst
LastPageFirst = QPrinter.LastPageFirst

Portrait = QPrinter.Portrait
Landscape = QPrinter.Landscape

ScreenResolution = QPrinter.ScreenResolution
PrinterResolution = QPrinter.PrinterResolution
HighResolution = QPrinter.HighResolution
