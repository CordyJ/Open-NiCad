# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the data for a switch operation.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_SvnSwitchDialog import Ui_SvnSwitchDialog

class SvnSwitchDialog(QDialog, Ui_SvnSwitchDialog):
    """
    Class implementing a dialog to enter the data for a switch operation.
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
       
        self.tagCombo.clear()
        self.tagCombo.addItems(taglist)
        
        if reposURL is not None and reposURL is not QString():
            self.tagCombo.setEditText(reposURL)
            
        if not standardLayout:
            self.TagTypeGroup.setEnabled(False)
        
    def getParameters(self):
        """
        Public method to retrieve the tag data.
        
        @return tuple of QString and int (tag, tag type)
        """
        tag = self.tagCombo.currentText()
        tagType = 0
        if self.regularButton.isChecked():
            tagType = 1
        elif self.branchButton.isChecked():
            tagType = 2
        if tag.isEmpty():
            tagType = 4
        return (tag, tagType)

