# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to edit breakpoint properties.
"""

import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4FileCompleter

from Ui_EditBreakpointDialog import Ui_EditBreakpointDialog

import Utilities

class EditBreakpointDialog(QDialog, Ui_EditBreakpointDialog):
    """
    Class implementing a dialog to edit breakpoint properties.
    """
    def __init__(self, id, properties, condHistory, parent = None, name = None, 
                 modal = False, addMode = False, filenameHistory = None):
        """
        Constructor
        
        @param id id of the breakpoint (tuple)
                (filename, linenumber)
        @param properties properties for the breakpoint (tuple)
                (condition, temporary flag, enabled flag, ignore count)
        @param condHistory the list of conditionals history (QStringList)
        @param parent the parent of this dialog
        @param name the widget name of this dialog
        @param modal flag indicating a modal dialog
        """
        QDialog.__init__(self,parent)
        self.setupUi(self)
        if name:
            self.setObjectName(name)
        self.setModal(modal)
        
        self.okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.filenameCompleter = E4FileCompleter(self.filenameCombo)
        
        fn, lineno = id
        
        if not addMode:
            cond, temp, enabled, count = properties
            
            # set the filename
            if fn is not None:
                self.filenameCombo.setEditText(fn)
            
            # set the line number
            self.linenoSpinBox.setValue(lineno)
            
            # set the condition
            if cond is None:
                cond = ''
            curr = condHistory.indexOf(cond)
            if curr == -1:
                condHistory.prepend(cond)
                curr = 0
            self.conditionCombo.addItems(condHistory)
            self.conditionCombo.setCurrentIndex(curr)
            
            # set the ignore count
            self.ignoreSpinBox.setValue(count)
            
            # set the checkboxes
            self.temporaryCheckBox.setChecked(temp)
            self.enabledCheckBox.setChecked(enabled)
            
            self.filenameCombo.setEnabled(False)
            self.fileButton.setEnabled(False)
            self.linenoSpinBox.setEnabled(False)
            self.conditionCombo.setFocus()
        else:
            self.setWindowTitle(self.trUtf8("Add Breakpoint"))
            # set the filename
            if fn is None:
                fn = QString('')
            curr = filenameHistory.indexOf(fn)
            if curr == -1:
                filenameHistory.prepend(fn)
                curr = 0
            self.filenameCombo.addItems(filenameHistory)
            self.filenameCombo.setCurrentIndex(curr)
            
            # set the condition
            cond = ''
            curr = condHistory.indexOf(cond)
            if curr == -1:
                condHistory.prepend(cond)
                curr = 0
            self.conditionCombo.addItems(condHistory)
            self.conditionCombo.setCurrentIndex(curr)
            
            if QString(fn).isEmpty():
                self.okButton.setEnabled(False)
        
    @pyqtSignature("")
    def on_fileButton_clicked(self):
        """
        Private slot to select a file via a file selection dialog.
        """
        file = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select filename of the breakpoint"),
            self.filenameCombo.currentText(),
            QString())
            
        if not file.isNull():
            self.filenameCombo.setEditText(Utilities.toNativeSeparators(file))
        
    def on_filenameCombo_editTextChanged(self, fn):
        """
        Private slot to handle the change of the filename.
        
        @param fn text of the filename edit (QString)
        """
        if fn.isEmpty():
            self.okButton.setEnabled(False)
        else:
            self.okButton.setEnabled(True)
        
    def getData(self):
        """
        Public method to retrieve the entered data.
        
        @return a tuple containing the breakpoints new properties
            (condition, temporary flag, enabled flag, ignore count)
        """
        return (self.conditionCombo.currentText(), 
                self.temporaryCheckBox.isChecked(),
                self.enabledCheckBox.isChecked(), self.ignoreSpinBox.value())
        
    def getAddData(self):
        """
        Public method to retrieve the entered data for an add.
        
        @return a tuple containing the new breakpoints properties
            (filename, lineno, condition, temporary flag, enabled flag, ignore count)
        """
        fn = self.filenameCombo.currentText()
        if fn.isEmpty():
            fn  =  None
        else:
            fn = os.path.expanduser(os.path.expandvars(unicode(fn)))
        
        return (fn, self.linenoSpinBox.value(), 
                self.conditionCombo.currentText(),
                self.temporaryCheckBox.isChecked(), self.enabledCheckBox.isChecked(),
                self.ignoreSpinBox.value())
