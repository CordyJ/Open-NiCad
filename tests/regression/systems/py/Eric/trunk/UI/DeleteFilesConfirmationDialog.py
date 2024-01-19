# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to confirm deletion of multiple files.
"""

from PyQt4.QtGui import QDialog, QDialogButtonBox

from Ui_DeleteFilesConfirmationDialog import Ui_DeleteFilesConfirmationDialog


class DeleteFilesConfirmationDialog(QDialog, Ui_DeleteFilesConfirmationDialog):
    """
    Class implementing a dialog to confirm deletion of multiple files.
    """
    def __init__(self, parent, caption, message, files):
        """
        Constructor
        
        @param parent parent of this dialog (QWidget)
        @param caption window title for the dialog (string or QString)
        @param message message to be shown (string or QString)
        @param okLabel label for the OK button (string or QString)
        @param cancelLabel label for the Cancel button (string or QString)
        @param files list of filenames to be shown (list of strings or QStrings
            or a QStringList)
        """
        QDialog.__init__(self,parent)
        self.setupUi(self)
        self.setModal(True)
        
        self.buttonBox.button(QDialogButtonBox.Yes).setAutoDefault(False)
        self.buttonBox.button(QDialogButtonBox.No).setDefault(True)
        self.buttonBox.button(QDialogButtonBox.No).setFocus()
        
        self.setWindowTitle(caption)
        self.message.setText(message)
        
        for file_ in files:
            self.filesList.addItem(file_)

    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.buttonBox.button(QDialogButtonBox.Yes):
            self.accept()
        elif button == self.buttonBox.button(QDialogButtonBox.No):
            self.reject()
