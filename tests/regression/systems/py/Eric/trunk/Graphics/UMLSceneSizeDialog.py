# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to set the scene sizes.
"""

from PyQt4.QtGui import QDialog

from Ui_UMLSceneSizeDialog import Ui_UMLSceneSizeDialog


class UMLSceneSizeDialog(QDialog, Ui_UMLSceneSizeDialog):
    """
    Class implementing a dialog to set the scene sizes.
    """
    def __init__(self, w, h, minW, minH, parent = None, name = None):
        """
        Constructor
        
        @param w current width of scene (integer)
        @param h current height of scene (integer)
        @param minW minimum width allowed (integer)
        @param minH minimum height allowed (integer)
        @param parent parent widget of this dialog (QWidget)
        @param name name of this widget (QString or string)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)
        
        self.widthSpinBox.setValue(w)
        self.heightSpinBox.setValue(h)
        self.widthSpinBox.setMinimum(minW)
        self.heightSpinBox.setMinimum(minH)
        self.widthSpinBox.selectAll()
        self.widthSpinBox.setFocus()
        
    def getData(self):
        """
        Method to retrieve the entered data.
        
        @return tuple giving the selected width and height
            (integer, integer)
        """
        return (self.widthSpinBox.value(), self.heightSpinBox.value())
