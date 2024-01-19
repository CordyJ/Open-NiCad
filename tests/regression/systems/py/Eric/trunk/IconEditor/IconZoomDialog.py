# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to select the zoom factor.
"""

from PyQt4.QtGui import QDialog

from Ui_IconZoomDialog import Ui_IconZoomDialog

class IconZoomDialog(QDialog, Ui_IconZoomDialog):
    """
    Class implementing a dialog to select the zoom factor.
    """
    def __init__(self, zoom, parent = None):
        """
        Constructor
        
        @param zoom zoom factor to show in the spinbox
        @param parent parent widget of this dialog (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.zoomSpinBox.setValue(zoom * 100)
        self.zoomSpinBox.selectAll()
        
    def getZoomFactor(self):
        """
        Public method to retrieve the zoom factor.
        
        @return zoom factor (int)
        """
        return self.zoomSpinBox.value() / 100
