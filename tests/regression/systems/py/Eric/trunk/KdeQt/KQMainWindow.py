# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Compatibility module to use the KDE main window instead of the Qt main window.
"""

import sys

from PyQt4.QtGui import QMainWindow

import Preferences

if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
    try:
        from PyKDE4.kdeui import KMainWindow
        
        class __kdeKQMainWindow(KMainWindow):
            """
            Compatibility class to use KMainWindow.
            """
            pass

    except (ImportError, RuntimeError):
        sys.e4nokde = True

class __qtKQMainWindow(QMainWindow):
    """
    Compatibility class to use QMainWindow.
    """
    pass

################################################################################

if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
    class KQMainWindow(__kdeKQMainWindow):
        """
        Compatibility class for the main window.
        """
        pass
else:
    class KQMainWindow(__qtKQMainWindow):
        """
        Compatibility class for the main window.
        """
        pass
