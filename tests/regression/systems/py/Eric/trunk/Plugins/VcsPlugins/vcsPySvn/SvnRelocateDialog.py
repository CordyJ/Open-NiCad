# -*- coding: utf-8 -*-

# Copyright (c)2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the data to relocate the workspace.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_SvnRelocateDialog import Ui_SvnRelocateDialog

class SvnRelocateDialog(QDialog, Ui_SvnRelocateDialog):
    """
    Class implementing a dialog to enter the data to relocate the workspace.
    """
    def __init__(self, currUrl, parent = None):
        """
        Constructor
        
        @param currUrl current repository URL (string or QString)
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.currUrlLabel.setText(currUrl)
        self.newUrlEdit.setText(currUrl)
        
    def getData(self):
        """
        Public slot used to retrieve the data entered into the dialog.
        
        @return the new repository URL (string) and an indication, if
            the relocate is inside the repository (boolean)
        """
        return unicode(self.newUrlEdit.text()), self.insideCheckBox.isChecked()
