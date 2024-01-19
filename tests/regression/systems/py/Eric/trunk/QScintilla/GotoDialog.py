# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Goto dialog.
"""

from PyQt4.QtGui import QDialog

from Ui_GotoDialog import Ui_GotoDialog

class GotoDialog(QDialog, Ui_GotoDialog):
    """
    Class implementing the Goto dialog.
    """
    def __init__(self, maximum, parent, name = None, modal = False):
        """
        Constructor
        
        @param maximum the maximum allowed for the spinbox (int)
        @param parent parent widget of this dialog (QWidget)
        @param name name of this dialog (string or QString)
        @param modal flag indicating a modal dialog (boolean)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)
        self.setModal(modal)
        
        self.linenumberSpinBox.setMaximum(maximum)
        self.linenumberSpinBox.selectAll()
        
    def getLinenumber(self):
        """
        Public method to retrieve the linenumber.
        
        @return line number (int)
        """
        return self.linenumberSpinBox.value()
