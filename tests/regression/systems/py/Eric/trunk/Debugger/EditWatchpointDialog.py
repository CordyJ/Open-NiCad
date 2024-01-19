# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to edit watch expression properties.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_EditWatchpointDialog import Ui_EditWatchpointDialog


class EditWatchpointDialog(QDialog, Ui_EditWatchpointDialog):
    """
    Class implementing a dialog to edit watch expression properties.
    """
    def __init__(self, properties, parent = None, name = None, modal = False):
        """
        Constructor
        
        @param properties properties for the watch expression (tuple)
            (expression, temporary flag, enabled flag, ignore count, special condition)
        @param parent the parent of this dialog
        @param name the widget name of this dialog
        @param modal flag indicating a modal dialog
        """
        QDialog.__init__(self,parent)
        self.setupUi(self)
        if name:
            self.setObjectName(name)
        self.setModal(modal)
        
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        
        # connect our widgets
        self.connect(self.conditionEdit, SIGNAL("textChanged(const QString &)"),
            self.__textChanged)
        self.connect(self.specialEdit, SIGNAL("textChanged(const QString &)"),
            self.__textChanged)
        
        cond, temp, enabled, count, special = properties
        
        # set the condition
        if special.isEmpty():
            self.conditionButton.setChecked(True)
            self.conditionEdit.setText(cond)
        else:
            self.specialButton.setChecked(True)
            self.specialEdit.setText(cond)
            ind = self.specialCombo.findText(special)
            if ind == -1:
                ind = 0
            self.specialCombo.setCurrentIndex(ind)
        
        # set the ignore count
        self.ignoreSpinBox.setValue(count)
        
        # set the checkboxes
        self.temporaryCheckBox.setChecked(temp)
        self.enabledCheckBox.setChecked(enabled)
        
        if special.isEmpty():
            self.conditionEdit.setFocus()
        else:
            self.specialEdit.setFocus()
        
    def __textChanged(self, txt):
        """
        Private slot to handle the text changed signal of the condition line edit.
        
        @param txt text of the line edit (QString)
        """
        if self.conditionButton.isChecked():
            self.buttonBox.button(QDialogButtonBox.Ok)\
                .setEnabled(not self.conditionEdit.text().isEmpty())
        elif self.specialButton.isChecked():
            self.buttonBox.button(QDialogButtonBox.Ok)\
                .setEnabled(not self.specialEdit.text().isEmpty())
        else:
            # should not happen
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        
        
    def getData(self):
        """
        Public method to retrieve the entered data.
        
        @return a tuple containing the watch expressions new properties
            (expression, temporary flag, enabled flag, ignore count, special condition)
        """
        if self.conditionButton.isChecked():
            return (self.conditionEdit.text(), 
                    self.temporaryCheckBox.isChecked(),
                    self.enabledCheckBox.isChecked(), 
                    self.ignoreSpinBox.value(),
                    QString(""))
        elif self.specialButton.isChecked():
            return (self.specialEdit.text(), 
                    self.temporaryCheckBox.isChecked(),
                    self.enabledCheckBox.isChecked(), 
                    self.ignoreSpinBox.value(),
                    self.specialCombo.currentText())
        else:
            # should not happen
            return (QString(""), False, False,  0, QString(""))
