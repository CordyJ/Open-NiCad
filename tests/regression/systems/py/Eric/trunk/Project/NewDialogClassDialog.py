# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to ente the data for a new dialog class file.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4DirCompleter

from Ui_NewDialogClassDialog import Ui_NewDialogClassDialog

class NewDialogClassDialog(QDialog, Ui_NewDialogClassDialog):
    """
    Class implementing a dialog to ente the data for a new dialog class file.
    """
    def __init__(self, defaultClassName, defaultFile, defaultPath, parent = None):
        """
        Constructor
        
        @param defaultClassName proposed name for the new class (string or QString)
        @param defaultFile proposed name for the source file (string or QString)
        @param defaultPath default path for the new file (string or QString)
        @param parent parent widget if the dialog (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.okButton.setEnabled(False)
        
        self.pathnameCompleter = E4DirCompleter(self.pathnameEdit)
        
        self.classnameEdit.setText(defaultClassName)
        self.filenameEdit.setText(defaultFile)
        self.pathnameEdit.setText(QDir.toNativeSeparators(defaultPath))
        
    @pyqtSignature("")
    def on_pathButton_clicked(self):
        """
        Private slot called to open a directory selection dialog.
        """
        path = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Select source directory"),
            QDir.fromNativeSeparators(self.pathnameEdit.text()),
            QFileDialog.Options(QFileDialog.Option(0)))
        if not path.isEmpty():
            self.pathnameEdit.setText(QDir.toNativeSeparators(path))
        
    def __enableOkButton(self):
        """
        Private slot to set the enable state of theok button.
        """
        self.okButton.setEnabled(\
            not self.classnameEdit.text().isEmpty() and \
            not self.filenameEdit.text().isEmpty() and \
            not self.pathnameEdit.text().isEmpty())
        
    def on_classnameEdit_textChanged(self, text):
        """
        Private slot called, when thext of the classname edit has changed.
        
        @param text changed text (QString)
        """
        self.__enableOkButton()
        
    def on_filenameEdit_textChanged(self, text):
        """
        Private slot called, when thext of the filename edit has changed.
        
        @param text changed text (QString)
        """
        self.__enableOkButton()
        
    def on_pathnameEdit_textChanged(self, text):
        """
        Private slot called, when thext of the pathname edit has changed.
        
        @param text changed text (QString)
        """
        self.__enableOkButton()
        
    def getData(self):
        """
        Public method to retrieve the data entered into the dialog.
        
        @return tuple giving the classname (string) and the file name (string)
        """
        return unicode(self.classnameEdit.text()), \
            os.path.join(unicode(self.pathnameEdit.text()), \
                         unicode(self.filenameEdit.text()))
