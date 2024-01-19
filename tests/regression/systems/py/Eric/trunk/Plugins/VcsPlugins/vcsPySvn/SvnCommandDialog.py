# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Subversion command dialog.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4DirCompleter

from Ui_SvnCommandDialog import Ui_SvnCommandDialog

import Utilities

class SvnCommandDialog(QDialog, Ui_SvnCommandDialog):
    """
    Class implementing the Subversion command dialog.
    
    It implements a dialog that is used to enter an
    arbitrary subversion command. It asks the user to enter
    the commandline parameters and the working directory.
    """
    def __init__(self, argvList, wdList, ppath, parent = None):
        """
        Constructor
        
        @param argvList history list of commandline arguments (QStringList)
        @param wdList history list of working directories (QStringList)
        @param ppath pathname of the project directory (string)
        @param parent parent widget of this dialog (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.workdirCompleter = E4DirCompleter(self.workdirCombo)
        
        self.okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.okButton.setEnabled(False)
        
        self.commandCombo.clear()
        self.commandCombo.addItems(argvList)
        if argvList.count() > 0:
            self.commandCombo.setCurrentIndex(0)
        self.workdirCombo.clear()
        self.workdirCombo.addItems(wdList)
        if wdList.count() > 0:
            self.workdirCombo.setCurrentIndex(0)
        self.projectDirLabel.setText(ppath)
        
        # modify some what's this help texts
        t = self.commandCombo.whatsThis()
        if not t.isEmpty():
            t = t.append(Utilities.getPercentReplacementHelp())
            self.commandCombo.setWhatsThis(t)
        
    @pyqtSignature("")
    def on_dirButton_clicked(self):
        """
        Private method used to open a directory selection dialog.
        """
        cwd = self.workdirCombo.currentText()
        if cwd.isEmpty():
            cwd = self.projectDirLabel.text()
        d = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Working directory"),
            cwd,
            QFileDialog.Options(QFileDialog.ShowDirsOnly))
        
        if not d.isEmpty():
            self.workdirCombo.setEditText(Utilities.toNativeSeparators(d))
        
    def on_commandCombo_editTextChanged(self, text):
        """
        Private method used to enable/disable the OK-button.
        
        @param text ignored
        """
        self.okButton.setDisabled(self.commandCombo.currentText().isEmpty())
    
    def getData(self):
        """
        Public method to retrieve the data entered into this dialog.
        
        @return a tuple of argv, workdir
        """
        return (self.commandCombo.currentText(),
                self.workdirCombo.currentText())
