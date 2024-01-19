# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the add project dialog.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4FileCompleter

from Ui_AddProjectDialog import Ui_AddProjectDialog

import Utilities

class AddProjectDialog(QDialog, Ui_AddProjectDialog):
    """
    Class implementing the add project dialog.
    """
    def __init__(self, parent = None, startdir = None, project = None):
        """
        Constructor
        
        @param parent parent widget of this dialog (QWidget)
        @param startdir start directory for the selection dialog (string or QString)
        @param project dictionary containing project data
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.fileCompleter = E4FileCompleter(self.filenameEdit)
        
        self.startdir = startdir
        
        self.__okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.__okButton.setEnabled(False)
        
        if project is not None:
            self.setWindowTitle(self.trUtf8("Project Properties"))
            
            self.filenameEdit.setReadOnly(True)
            self.fileButton.setEnabled(False)
            
            self.nameEdit.setText(project['name'])
            self.filenameEdit.setText(project['file'])
            self.descriptionEdit.setPlainText(project['description'])
            self.masterCheckBox.setChecked(project['master'])
    
    @pyqtSignature("")
    def on_fileButton_clicked(self):
        """
        Private slot to display a file selection dialog.
        """
        startdir = self.filenameEdit.text()
        if startdir.isEmpty() and self.startdir is not None:
            startdir = self.startdir
            projectFile = KQFileDialog.getOpenFileName(\
                self,
                self.trUtf8("Add Project"),
                startdir,
                self.trUtf8("Project Files (*.e4p *.e4pz)"),
                None)
        
        if not projectFile.isEmpty():
            self.filenameEdit.setText(Utilities.toNativeSeparators(projectFile))
    
    def getData(self):
        """
        Public slot to retrieve the dialogs data.
        
        @return tuple of four values (string, string, boolean, string) giving the 
            project name, the name of the project file, a flag telling, whether
            the project shall be the master project and a short description
            for the project
        """
        return (unicode(self.nameEdit.text()), unicode(self.filenameEdit.text()), 
                self.masterCheckBox.isChecked(), 
                unicode(self.descriptionEdit.toPlainText()))
    
    @pyqtSignature("QString")
    def on_nameEdit_textChanged(self, p0):
        """
        Private slot called when the project name has changed.
        """
        self.__updateUi()
    
    @pyqtSignature("QString")
    def on_filenameEdit_textChanged(self, p0):
        """
        Private slot called when the project filename has changed.
        """
        self.__updateUi()
    
    def __updateUi(self):
        """
        Private method to update the dialog.
        """
        self.__okButton.setEnabled(not self.nameEdit.text().isEmpty() and \
                                   not self.filenameEdit.text().isEmpty())
