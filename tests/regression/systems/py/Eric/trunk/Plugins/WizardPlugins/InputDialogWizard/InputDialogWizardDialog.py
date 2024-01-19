# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the input dialog wizard dialog.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQApplication import e4App

from Ui_InputDialogWizardDialog import Ui_InputDialogWizardDialog

class InputDialogWizardDialog(QDialog, Ui_InputDialogWizardDialog):
    """
    Class implementing the input dialog wizard dialog.
    
    It displays a dialog for entering the parameters
    for the QInputDialog code generator.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        # set the validators for the double line edots
        self.eDoubleDefault.setValidator(\
            QDoubleValidator(-2147483647, 2147483647, 99, self.eDoubleDefault))
        self.eDoubleFrom.setValidator(\
            QDoubleValidator(-2147483647, 2147483647, 99, self.eDoubleFrom))
        self.eDoubleTo.setValidator(\
            QDoubleValidator(-2147483647, 2147483647, 99, self.eDoubleTo))
        
        self.bTest = \
            self.buttonBox.addButton(self.trUtf8("Test"), QDialogButtonBox.ActionRole)
        
    @pyqtSignature("bool")
    def on_rItem_toggled(self, checked):
        """
        Private slot to perform actions dependant on the item type selection.
        
        @param checked flag indicating the checked state (boolean)
        """
        self.bTest.setEnabled(not checked)
        
    def on_buttonBox_clicked(self, button):
        """
        Private slot called by a button of the button box clicked.
        
        @param button button that was clicked (QAbstractButton)
        """
        if button == self.bTest:
            self.on_bTest_clicked()
    
    @pyqtSignature("")
    def on_bTest_clicked(self):
        """
        Private method to test the selected options.
        """
        if self.rText.isChecked():
            if self.rEchoNormal.isChecked():
                echomode = QLineEdit.Normal
            elif self.rEchoNoEcho.isChecked():
                echomode = QLineEdit.NoEcho
            else:
                echomode = QLineEdit.Password
            QInputDialog.getText(\
                None,
                self.eCaption.text(),
                self.eLabel.text(),
                echomode,
                self.eTextDefault.text())
        elif self.rInteger.isChecked():
            QInputDialog.getInteger(\
                None,
                self.eCaption.text(),
                self.eLabel.text(),
                self.sIntDefault.value(),
                self.sIntFrom.value(),
                self.sIntTo.value(),
                self.sIntStep.value())
        elif self.rDouble.isChecked():
            try:
                doubleDefault = float(str(self.eDoubleDefault.text()))
            except ValueError:
                doubleDefault = 0
            try:
                doubleFrom = float(str(self.eDoubleFrom.text()))
            except ValueError:
                doubleFrom = -2147483647
            try:
                doubleTo = float(str(self.eDoubleTo.text()))
            except ValueError:
                doubleTo = 2147483647
            QInputDialog.getDouble(\
                None,
                self.eCaption.text(),
                self.eLabel.text(),
                doubleDefault,
                doubleFrom,
                doubleTo,
                self.sDoubleDecimals.value())
        
    def __getCode4(self, indLevel, indString):
        """
        Private method to get the source code for Qt4.
        
        @param indLevel indentation level (int)
        @param indString string used for indentation (space or tab) (string)
        @return generated code (string)
        """
        # calculate our indentation level and the indentation string
        il = indLevel + 1
        istring = il * indString
        
        # now generate the code
        code = 'QInputDialog.'
        if self.rText.isChecked():
            code += 'getText(\\%s%s' % (os.linesep, istring)
            code += 'None,%s%s' % (os.linesep, istring)
            code += 'self.trUtf8("%s"),%s%s' % \
                (unicode(self.eCaption.text()), os.linesep, istring)
            code += 'self.trUtf8("%s"),%s%s' % \
                (unicode(self.eLabel.text()), os.linesep, istring)
            if self.rEchoNormal.isChecked():
                code += 'QLineEdit.Normal'
            elif self.rEchoNoEcho.isChecked():
                code += 'QLineEdit.NoEcho'
            else:
                code += 'QLineEdit.Password'
            if not self.eTextDefault.text().isEmpty():
                code += ',%s%sself.trUtf8("%s")' % \
                    (os.linesep, istring, unicode(self.eTextDefault.text()))
            code += ')%s' % os.linesep
        elif self.rInteger.isChecked():
            code += 'getInteger(\\%s%s' % (os.linesep, istring)
            code += 'None,%s%s' % (os.linesep, istring)
            code += 'self.trUtf8("%s"),%s%s' % \
                (unicode(self.eCaption.text()), os.linesep, istring)
            code += 'self.trUtf8("%s"),%s%s' % \
                (unicode(self.eLabel.text()), os.linesep, istring)
            code += '%d, %d, %d, %d)%s' % \
                (self.sIntDefault.value(), self.sIntFrom.value(),
                self.sIntTo.value(), self.sIntStep.value(), os.linesep)
        elif self.rDouble.isChecked():
            try:
                doubleDefault = float(str(self.eDoubleDefault.text()))
            except ValueError:
                doubleDefault = 0
            try:
                doubleFrom = float(str(self.eDoubleFrom.text()))
            except ValueError:
                doubleFrom = -2147483647
            try:
                doubleTo = float(str(self.eDoubleTo.text()))
            except ValueError:
                doubleTo = 2147483647
            code += 'getDouble(\\%s%s' % (os.linesep, istring)
            code += 'None,%s%s' % (os.linesep, istring)
            code += 'self.trUtf8("%s"),%s%s' % \
                (unicode(self.eCaption.text()), os.linesep, istring)
            code += 'self.trUtf8("%s"),%s%s' % \
                (unicode(self.eLabel.text()), os.linesep, istring)
            code += '%s, %s, %s, %d)%s' % \
                (str(doubleDefault), str(doubleFrom), str(doubleTo), 
                self.sDoubleDecimals.value(), os.linesep)
        elif self.rItem.isChecked():
            code += 'getItem(\\%s%s' % (os.linesep, istring)
            code += 'None,%s%s' % (os.linesep, istring)
            code += 'self.trUtf8("%s"),%s%s' % \
                (unicode(self.eCaption.text()), os.linesep, istring)
            code += 'self.trUtf8("%s"),%s%s' % \
                (unicode(self.eLabel.text()), os.linesep, istring)
            code += '%s,%s%s' % (unicode(self.eVariable.text()), os.linesep, istring)
            code += '%d, %s)%s' % \
                (self.sCurrentItem.value(), self.cEditable.isChecked(), os.linesep)
            
        return code
        
    def getCode(self, indLevel, indString):
        """
        Public method to get the source code.
        
        @param indLevel indentation level (int)
        @param indString string used for indentation (space or tab) (string)
        @return generated code (string)
        """
        return self.__getCode4(indLevel, indString)
