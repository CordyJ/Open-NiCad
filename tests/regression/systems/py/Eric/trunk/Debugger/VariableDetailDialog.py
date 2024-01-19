# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the variable detail dialog.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_VariableDetailDialog import Ui_VariableDetailDialog

class VariableDetailDialog(QDialog, Ui_VariableDetailDialog):
    """
    Class implementing the variable detail dialog.
    
    This dialog shows the name, the type and the value of a variable
    in a read only dialog. It is opened upon a double click in the
    variables viewer widget.
    """
    def __init__(self, var, vtype, value):
        """
        Constructor
        
        @param var the variables name (string or QString)
        @param vtype the variables type (string or QString)
        @param value the variables value (string or QString)
        """
        QDialog.__init__(self)
        self.setupUi(self)
        
        # set the different fields
        self.eName.setText(var)
        self.eType.setText(vtype)
        self.eValue.setPlainText(value)
