# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a zoom dialog for a graphics canvas.
"""

from PyQt4.QtGui import QDialog

from Ui_ZoomDialog import Ui_ZoomDialog

class ZoomDialog(QDialog, Ui_ZoomDialog):
    """
    Class implementing a zoom dialog for a graphics canvas.
    """
    def __init__(self, zoom, parent = None, name = None):
        """
        Constructor
        
        @param zoom zoom factor to show in the spinbox (float)
        @param parent parent widget of this dialog (QWidget)
        @param name name of this dialog (string or QString)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        else:
            self.setObjectName("ZoomDialog")
        self.setupUi(self)
        self.zoomSpinBox.setValue(zoom)
        
    def getZoomSize(self):
        """
        Public method to retrieve the zoom size.
        
        @return zoom size (double)
        """
        return self.zoomSpinBox.value()
