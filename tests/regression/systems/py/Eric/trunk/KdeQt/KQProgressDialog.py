# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Compatibility module to use the KDE Progress Dialog instead of the Qt Progress Dialog.
"""

import sys

from PyQt4.QtCore import Qt

import Preferences

if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
    try:
        from PyKDE4.kdeui import KProgressDialog
        from PyQt4.QtCore import QString
        
        class __kdeKQProgressDialog(KProgressDialog):
            """
            Compatibility class to use the KDE Progress Dialog instead of 
            the Qt Progress Dialog.
            """
            def __init__(self, labelText, cancelButtonText, minimum, maximum,
                         parent = None, f = Qt.WindowFlags(Qt.Widget)):
                """
                Constructor
                
                @param labelText text to show in the progress dialog (QString)
                @param cancelButtonText text to show for the cancel button or
                    None to disallow cancellation and to hide the cancel button (QString)
                @param minimum minimum value for the progress indicator (integer)
                @param maximum maximum value for the progress indicator (integer)
                @param parent parent of the progress dialog (QWidget)
                @param f window flags (ignored) (Qt.WindowFlags)
                """
                KProgressDialog.__init__(self, parent, QString(), labelText, f)
                self.__bar = self.progressBar()
                self.__bar.setMinimum(minimum)
                self.__bar.setMaximum(maximum)
                if cancelButtonText is None or QString(cancelButtonText).isEmpty():
                    self.setAllowCancel(False)
                else:
                    self.setAllowCancel(True)
                    self.setButtonText(cancelButtonText)
            
            def reset(self):
                """
                Public slot to reset the progress bar.
                """
                self.__bar.reset()
                if self.autoClose():
                    self.close()
            
            def setLabel(self, label):
                """
                Public method to set the dialog's label.
                
                Note: This is doing nothing.
                
                @param label label to be set (QLabel)
                """
                pass
            
            def setMinimum(self, minimum):
                """
                Public slot to set the minimum value of the progress bar.
                
                @param minimum minimum value for the progress indicator (integer)
                """
                self.__bar.setMinimum(minimum)
            
            def setMaximum(self, maximum):
                """
                Public slot to set the maximum value of the progress bar.
                
                @param maximum maximum value for the progress indicator (integer)
                """
                self.__bar.setMaximum(maximum)
            
            def setValue(self, value):
                """
                Public slot to set the current value of the progress bar.
                
                @param value progress value to set
                """
                self.__bar.setValue(value)
            
            def wasCanceled(self):
                """
                Public slot to check, if the dialog was canceled.
                
                @return flag indicating, if the dialog was canceled (boolean)
                """
                return self.wasCancelled()

    except (ImportError, RuntimeError):
        sys.e4nokde = True

from PyQt4.QtGui import QProgressDialog
class __qtKQProgressDialog(QProgressDialog):
    """
    Compatibility class to use the Qt Progress Dialog.
    """
    pass

################################################################################

def KQProgressDialog(labelText, cancelButtonText, minimum, maximum, 
                     parent = None, f = Qt.WindowFlags(Qt.Widget)):
    """
    Public function to instantiate a progress dialog object.
    
    @param labelText text to show in the progress dialog (QString)
    @param cancelButtonText text to show for the cancel button or
        None to disallow cancellation and to hide the cancel button (QString)
    @param minimum minimum value for the progress indicator (integer)
    @param maximum maximum value for the progress indicator (integer)
    @param parent reference to the parent widget (QWidget)
    @param f window flags for the dialog (Qt.WindowFlags)
    @return reference to the progress dialog object
    """
    if Preferences.getUI("UseKDEDialogs") and not sys.e4nokde:
        return __kdeKQProgressDialog(labelText, cancelButtonText, 
                                     minimum, maximum, parent, f)
    else:
        return __qtKQProgressDialog(labelText, cancelButtonText, 
                                    minimum, maximum, parent, f)
