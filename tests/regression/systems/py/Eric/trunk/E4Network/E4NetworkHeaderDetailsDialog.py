# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show the data of a response or reply header.
"""

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature

from Ui_E4NetworkHeaderDetailsDialog import Ui_E4NetworkHeaderDetailsDialog

class E4NetworkHeaderDetailsDialog(QDialog, Ui_E4NetworkHeaderDetailsDialog):
    """
    Class implementing a dialog to show the data of a response or reply header.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
    
    def setData(self, name, value):
        """
        Public method to set the data to display.
        
        @param name name of the header (string or QString)
        @param value value of the header (string or QString)
        """
        self.nameEdit.setText(name)
        self.valueEdit.setPlainText(value)
