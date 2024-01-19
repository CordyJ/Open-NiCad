# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the data for a tagging operation.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_SvnTagDialog import Ui_SvnTagDialog

class SvnTagDialog(QDialog, Ui_SvnTagDialog):
    """
    Class implementing a dialog to enter the data for a tagging operation.
    """
    def __init__(self, taglist, reposURL, standardLayout, parent = None):
        """
        Constructor
        
        @param taglist list of previously entered tags (QStringList)
        @param reposURL repository path (QString or string) or None
        @param standardLayout flag indicating the layout of the 
            repository (boolean)
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.okButton.setEnabled(False)
       
        self.tagCombo.clear()
        self.tagCombo.addItems(taglist)
        
        if reposURL is not None and reposURL is not QString():
            self.tagCombo.setEditText(reposURL)
        
        if not standardLayout:
            self.TagActionGroup.setEnabled(False)
        
    def on_tagCombo_editTextChanged(self, text):
        """
        Private method used to enable/disable the OK-button.
        
        @param text ignored
        """
        self.okButton.setDisabled(text.isEmpty())
    
    def getParameters(self):
        """
        Public method to retrieve the tag data.
        
        @return tuple of QString and int (tag, tag operation)
        """
        tag = self.tagCombo.currentText()
        tagOp = 0
        if self.createRegularButton.isChecked():
            tagOp = 1
        elif self.createBranchButton.isChecked():
            tagOp = 2
        elif self.deleteRegularButton.isChecked():
            tagOp = 4
        elif self.deleteBranchButton.isChecked():
            tagOp = 8
        return (tag, tagOp)
