# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the data for a new property.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_SvnPropDelDialog import Ui_SvnPropDelDialog

class SvnPropDelDialog(QDialog, Ui_SvnPropDelDialog):
    """
    Class implementing a dialog to enter the data for a new property.
    """
    def __init__(self, recursive, parent = None):
        """
        Constructor
        
        @param recursive flag indicating a recursive set is requested
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.okButton.setEnabled(False)
        
        self.recurseCheckBox.setChecked(recursive)
        
    def on_propNameEdit_textChanged(self, text):
        """
        Private method used to enable/disable the OK-button.
        
        @param text ignored
        """
        self.okButton.setDisabled(text.isEmpty())
    
    def getData(self):
        """
        Public slot used to retrieve the data entered into the dialog.
        
        @return tuple of two values giving the property name and a flag 
            indicating, that this property should be applied recursively.
            (string, boolean)
        """
        return (unicode(self.propNameEdit.text()), 
                self.recurseCheckBox.isChecked())
