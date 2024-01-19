# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Compatibility module to use the KDE Input Dialog instead of the Qt Input Dialog.
"""

import sys

import Preferences

if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
    try:
        from PyKDE4.kdeui import KInputDialog, KPasswordDialog
        from PyQt4.QtCore import QString, Qt
        from PyQt4.QtGui import QLineEdit
        
        def __kdeGetText(parent, title, label, mode = QLineEdit.Normal, text = QString(),
                         f = Qt.WindowFlags(Qt.Widget)):
            """
            Function to get some text from the user.
            
            @param parent parent widget of the dialog (QWidget)
            @param title window title of the dialog (QString)
            @param label text of the label for the line edit (QString)
            @param mode mode of the line edit (QLineEdit.EchoMode)
            @param text initial text of the line edit (QString)
            @param f window flags for the dialog (Qt.WindowFlags)
            @return tuple of (text, ok). text contains the text entered by the
                user, ok indicates a valid input. (QString, boolean)
            """
            if mode == QLineEdit.Normal:
                return KInputDialog.getText(title, label, text, parent)
            else:
                dlg = KPasswordDialog(parent)
                dlg.setWindowTitle(title)
                dlg.setPrompt(label)
                if not text.isEmpty():
                    dlg.setPassword(text)
                if dlg.exec_() == KPasswordDialog.Accepted:
                    ok = True
                    password = dlg.password()
                else:
                    ok = False
                    password = QString()
                return password, ok
        
        def __kdeGetInteger(parent, title, label, value = 0, minValue = -2147483647, 
                            maxValue = 2147483647, step = 1, f = Qt.WindowFlags(Qt.Widget)):
            """
            Function to get an integer value from the user.
            
            @param parent parent widget of the dialog (QWidget)
            @param title window title of the dialog (QString)
            @param label text of the label for the line edit (QString)
            @param value initial value of the spin box (integer)
            @param minValue minimal value of the spin box (integer)
            @param maxValue maximal value of the spin box (integer)
            @param step step size of the spin box (integer)
            @param f window flags for the dialog (Qt.WindowFlags)
            @return tuple of (value, ok). value contains the integer entered by the
                user, ok indicates a valid input. (integer, boolean)
            """
            return KInputDialog.getInteger(title, label, value, minValue, maxValue, step,
                                           10, parent)
        
        def __kdeGetDouble(parent, title, label, value = 0.0, 
                           minValue = -2147483647.0, maxValue = 2147483647.0, decimals = 1, 
                           f = Qt.WindowFlags(Qt.Widget)):
            """
            Function to get a double value from the user.
            
            @param parent parent widget of the dialog (QWidget)
            @param title window title of the dialog (QString)
            @param label text of the label for the line edit (QString)
            @param value initial value of the spin box (double)
            @param minValue minimal value of the spin box (double)
            @param maxValue maximal value of the spin box (double)
            @param decimals maximum number of decimals the value may have (integer)
            @param f window flags for the dialog (Qt.WindowFlags)
            @return tuple of (value, ok). value contains the double entered by the
                user, ok indicates a valid input. (double, boolean)
            """
            return KInputDialog.getDouble(title, label, value, minValue, maxValue, decimals,
                                          parent)
        
        def __kdeGetItem(parent, title, label, slist, current = 0, editable = True, 
                         f = Qt.WindowFlags(Qt.Widget)):
            """
            Function to get an item of a list from the user.
            
            @param parent parent widget of the dialog (QWidget)
            @param title window title of the dialog (QString)
            @param label text of the label for the line edit (QString)
            @param slist list of strings to select from (QStringList)
            @param current number of item, that should be selected as a default (integer)
            @param editable indicates whether the user can input their own text (boolean)
            @param f window flags for the dialog (Qt.WindowFlags)
            @return tuple of (value, ok). value contains the double entered by the
                user, ok indicates a valid input. (QString, boolean)
            """
            return KInputDialog.getItem(title, label, slist, current, editable, parent)
        
    except (ImportError, RuntimeError):
        sys.e4nokde = True

import PyQt4.QtGui

__qtGetText = PyQt4.QtGui.QInputDialog.getText
__qtGetInteger = PyQt4.QtGui.QInputDialog.getInteger
__qtGetDouble = PyQt4.QtGui.QInputDialog.getDouble
__qtGetItem = PyQt4.QtGui.QInputDialog.getItem

################################################################################

from PyQt4.QtCore import QString, Qt
from PyQt4.QtGui import QLineEdit

def getText(parent, title, label, mode = QLineEdit.Normal, text = QString(),
            f = Qt.WindowFlags(Qt.Widget)):
    """
    Function to get some text from the user.
    
    @param parent parent widget of the dialog (QWidget)
    @param title window title of the dialog (QString)
    @param label text of the label for the line edit (QString)
    @param mode mode of the line edit (QLineEdit.EchoMode)
    @param text initial text of the line edit (QString)
    @param f window flags for the dialog (Qt.WindowFlags)
    @return tuple of (text, ok). text contains the text entered by the
        user, ok indicates a valid input. (QString, boolean)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeGetText(parent, title, label, mode, text, f)
    else:
        return __qtGetText(parent, title, label, mode, text, f)

def getInteger(parent, title, label, value = 0, minValue = -2147483647, 
               maxValue = 2147483647, step = 1, f = Qt.WindowFlags(Qt.Widget)):
    """
    Function to get an integer value from the user.
    
    @param parent parent widget of the dialog (QWidget)
    @param title window title of the dialog (QString)
    @param label text of the label for the line edit (QString)
    @param value initial value of the spin box (integer)
    @param minValue minimal value of the spin box (integer)
    @param maxValue maximal value of the spin box (integer)
    @param step step size of the spin box (integer)
    @param f window flags for the dialog (Qt.WindowFlags)
    @return tuple of (value, ok). value contains the integer entered by the
        user, ok indicates a valid input. (integer, boolean)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeGetInteger(parent, title, label, value, minValue, maxValue, step, f)
    else:
        return __qtGetInteger(parent, title, label, value, minValue, maxValue, step, f)

def getDouble(parent, title, label, value = 0.0, minValue = -2147483647.0, 
              maxValue = 2147483647.0, decimals = 1, f = Qt.WindowFlags(Qt.Widget)):
    """
    Function to get a double value from the user.
    
    @param parent parent widget of the dialog (QWidget)
    @param title window title of the dialog (QString)
    @param label text of the label for the line edit (QString)
    @param value initial value of the spin box (double)
    @param minValue minimal value of the spin box (double)
    @param maxValue maximal value of the spin box (double)
    @param decimals maximum number of decimals the value may have (integer)
    @param f window flags for the dialog (Qt.WindowFlags)
    @return tuple of (value, ok). value contains the double entered by the
        user, ok indicates a valid input. (double, boolean)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeGetDouble(parent, title, label, value, 
                              minValue, maxValue, decimals, f)
    else:
        return __qtGetDouble(parent, title, label, value, 
                             minValue, maxValue, decimals, f)

def getItem(parent, title, label, slist, current = 0, editable = True, 
            f = Qt.WindowFlags(Qt.Widget)):
    """
    Function to get an item of a list from the user.
    
    @param parent parent widget of the dialog (QWidget)
    @param title window title of the dialog (QString)
    @param label text of the label for the line edit (QString)
    @param slist list of strings to select from (QStringList)
    @param current number of item, that should be selected as a default (integer)
    @param editable indicates whether the user can input their own text (boolean)
    @param f window flags for the dialog (Qt.WindowFlags)
    @return tuple of (value, ok). value contains the double entered by the
        user, ok indicates a valid input. (QString, boolean)
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeGetItem(parent, title, label, slist, current, editable, f)
    else:
        return __qtGetItem(parent, title, label, slist, current, editable, f)
