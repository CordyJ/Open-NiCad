# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the multi project properties dialog.
"""

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature

from Ui_PropertiesDialog import Ui_PropertiesDialog

class PropertiesDialog(QDialog, Ui_PropertiesDialog):
    """
    Class implementing the multi project properties dialog.
    """
    def __init__(self, multiProject, new = True, parent = None):
        """
        Constructor
        
        @param multiProject reference to the multi project object
        @param new flag indicating the generation of a new multi project
        @param parent parent widget of this dialog (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.multiProject = multiProject
        self.newMultiProject = new
        
        if not new:
            self.descriptionEdit.setPlainText(self.multiProject.description)
    
    def storeData(self):
        """
        Public method to store the entered/modified data.
        """
        self.multiProject.description = unicode(self.descriptionEdit.toPlainText())
