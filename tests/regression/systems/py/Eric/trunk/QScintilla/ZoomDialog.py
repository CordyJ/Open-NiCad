# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to select the zoom scale.
"""

from PyQt4.QtGui import QDialog

from Ui_ZoomDialog import Ui_ZoomDialog

class ZoomDialog(QDialog, Ui_ZoomDialog):
    """
    Class implementing a dialog to select the zoom scale.
    """
    def __init__(self, zoom, parent, name = None, modal = False):
        """
        Constructor
        
        @param zoom zoom factor to show in the spinbox
        @param parent parent widget of this dialog (QWidget)
        @param name name of this dialog (string or QString)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)
        self.setModal(modal)
        
        self.zoomSpinBox.setValue(zoom)
        self.zoomSpinBox.selectAll()
        
    def getZoomSize(self):
        """
        Public method to retrieve the zoom size.
        
        @return zoom size (int)
        """
        return self.zoomSpinBox.value()
