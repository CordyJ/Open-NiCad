# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the message box wizard dialog.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQApplication import e4App

from Ui_MessageBoxWizardDialog import Ui_MessageBoxWizardDialog

class MessageBoxWizardDialog(QDialog, Ui_MessageBoxWizardDialog):
    """
    Class implementing the message box wizard dialog.
    
    It displays a dialog for entering the parameters
    for the QMessageBox code generator.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        # keep the following three lists in sync
        self.buttonsList = QStringList() \
            << self.trUtf8("No button") \
            << self.trUtf8("Abort") \
            << self.trUtf8("Apply") \
            << self.trUtf8("Cancel") \
            << self.trUtf8("Close") \
            << self.trUtf8("Discard") \
            << self.trUtf8("Help") \
            << self.trUtf8("Ignore") \
            << self.trUtf8("No") \
            << self.trUtf8("No to all") \
            << self.trUtf8("Ok") \
            << self.trUtf8("Open") \
            << self.trUtf8("Reset") \
            << self.trUtf8("Restore defaults") \
            << self.trUtf8("Retry") \
            << self.trUtf8("Save") \
            << self.trUtf8("Save all") \
            << self.trUtf8("Yes") \
            << self.trUtf8("Yes to all")
        self.buttonsCodeListBinary = [
            QMessageBox.NoButton,
            QMessageBox.Abort,
            QMessageBox.Apply,
            QMessageBox.Cancel,
            QMessageBox.Close,
            QMessageBox.Discard,
            QMessageBox.Help,
            QMessageBox.Ignore,
            QMessageBox.No,
            QMessageBox.NoToAll,
            QMessageBox.Ok,
            QMessageBox.Open,
            QMessageBox.Reset,
            QMessageBox.RestoreDefaults,
            QMessageBox.Retry,
            QMessageBox.Save,
            QMessageBox.SaveAll,
            QMessageBox.Yes,
            QMessageBox.YesToAll,
        ]
        self.buttonsCodeListText = [
            "QMessageBox.NoButton",
            "QMessageBox.Abort",
            "QMessageBox.Apply",
            "QMessageBox.Cancel",
            "QMessageBox.Close",
            "QMessageBox.Discard",
            "QMessageBox.Help",
            "QMessageBox.Ignore",
            "QMessageBox.No",
            "QMessageBox.NoToAll",
            "QMessageBox.Ok",
            "QMessageBox.Open",
            "QMessageBox.Reset",
            "QMessageBox.RestoreDefaults",
            "QMessageBox.Retry",
            "QMessageBox.Save",
            "QMessageBox.SaveAll",
            "QMessageBox.Yes",
            "QMessageBox.YesToAll",
        ]
        
        self.defaultCombo.addItems(self.buttonsList)
        
        self.bTest = \
            self.buttonBox.addButton(self.trUtf8("Test"), QDialogButtonBox.ActionRole)
        
        if qVersion() < "4.2.0":
            self.rQt4.setChecked(True)
        else:
            self.rQt42.setChecked(True)
        
    def __testQt40(self):
        """
        Private method to test the selected options for Qt3 and Qt 4.0.
        """
        b1 = QString()
        b2 = QString()
        b3 = QString()
        if not self.cButton0.currentText().isEmpty():
            b1 = self.cButton0.currentText()
            if not self.cButton1.currentText().isEmpty():
                b2 = self.cButton1.currentText()
                if not self.cButton2.currentText().isEmpty():
                    b3 = self.cButton2.currentText()
            
        if self.rInformation.isChecked():
            QMessageBox.information(None,
                self.eCaption.text(),
                self.eMessage.toPlainText(),
                b1, b2, b3, 
                self.sDefault.value(),
                self.sEscape.value()
            )
        elif self.rQuestion.isChecked():
            QMessageBox.question(None,
                self.eCaption.text(),
                self.eMessage.toPlainText(),
                b1, b2, b3, 
                self.sDefault.value(),
                self.sEscape.value()
            )
        elif self.rWarning.isChecked(): 
            QMessageBox.warning(None,
                self.eCaption.text(),
                self.eMessage.toPlainText(),
                b1, b2, b3, 
                self.sDefault.value(),
                self.sEscape.value()
            )
        elif self.rCritical.isChecked():
            QMessageBox.critical(None,
                self.eCaption.text(),
                self.eMessage.toPlainText(),
                b1, b2, b3, 
                self.sDefault.value(),
                self.sEscape.value()
            )
    
    def __testQt42(self):
        """
        Private method to test the selected options for Qt 4.2.0.
        """
        buttons = QMessageBox.NoButton
        if self.abortCheck.isChecked():
            buttons |= QMessageBox.Abort
        if self.applyCheck.isChecked():
            buttons |= QMessageBox.Apply
        if self.cancelCheck.isChecked():
            buttons |= QMessageBox.Cancel
        if self.closeCheck.isChecked():
            buttons |= QMessageBox.Close
        if self.discardCheck.isChecked():
            buttons |= QMessageBox.Discard
        if self.helpCheck.isChecked():
            buttons |= QMessageBox.Help
        if self.ignoreCheck.isChecked():
            buttons |= QMessageBox.Ignore
        if self.noCheck.isChecked():
            buttons |= QMessageBox.No
        if self.notoallCheck.isChecked():
            buttons |= QMessageBox.NoToAll
        if self.okCheck.isChecked():
            buttons |= QMessageBox.Ok
        if self.openCheck.isChecked():
            buttons |= QMessageBox.Open
        if self.resetCheck.isChecked():
            buttons |= QMessageBox.Reset
        if self.restoreCheck.isChecked():
            buttons |= QMessageBox.RestoreDefaults
        if self.retryCheck.isChecked():
            buttons |= QMessageBox.Retry
        if self.saveCheck.isChecked():
            buttons |= QMessageBox.Save
        if self.saveallCheck.isChecked():
            buttons |= QMessageBox.SaveAll
        if self.yesCheck.isChecked():
            buttons |= QMessageBox.Yes
        if self.yestoallCheck.isChecked():
            buttons |= QMessageBox.YesToAll
        if buttons == QMessageBox.NoButton:
            buttons = QMessageBox.Ok
        
        defaultButton = self.buttonsCodeListBinary[self.defaultCombo.currentIndex()]
        
        if self.rInformation.isChecked():
            QMessageBox.information(None,
                self.eCaption.text(),
                self.eMessage.toPlainText(),
                QMessageBox.StandardButtons(buttons),
                defaultButton
            )
        elif self.rQuestion.isChecked():
            QMessageBox.question(None,
                self.eCaption.text(),
                self.eMessage.toPlainText(),
                QMessageBox.StandardButtons(buttons),
                defaultButton
            )
        elif self.rWarning.isChecked(): 
            QMessageBox.warning(None,
                self.eCaption.text(),
                self.eMessage.toPlainText(),
                QMessageBox.StandardButtons(buttons),
                defaultButton
            )
        elif self.rCritical.isChecked():
            QMessageBox.critical(None,
                self.eCaption.text(),
                self.eMessage.toPlainText(),
                QMessageBox.StandardButtons(buttons),
                defaultButton
            )
    
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
        if self.rAbout.isChecked():
            QMessageBox.about(None,
                self.eCaption.text(),
                self.eMessage.toPlainText()
            )
        elif self.rAboutQt.isChecked():
            QMessageBox.aboutQt(None,
                self.eCaption.text()
            )
        else:
            if self.rQt42.isChecked():
                self.__testQt42()
            else:
                self.__testQt40()
        
    def on_cButton0_editTextChanged(self, text):
        """
        Private slot to enable/disable the other button combos depending on its contents.
        
        @param text the new text (QString)
        """
        if text.isEmpty():
            self.cButton1.setEnabled(False)
            self.cButton2.setEnabled(False)
        else:
            self.cButton1.setEnabled(True)
            if self.cButton1.currentText().isEmpty():
                self.cButton2.setEnabled(False)
            else:
                self.cButton2.setEnabled(True)
        self.sDefault.setMaximum(0)
        self.sEscape.setMaximum(0)

    def on_cButton1_editTextChanged(self, text):
        """
        Private slot to enable/disable the other button combos depending on its contents.
        
        @param text the new text (QString)
        """
        if text.isEmpty():
            self.cButton2.setEnabled(False)
            self.sDefault.setMaximum(0)
            self.sEscape.setMaximum(0)
        else:
            self.cButton2.setEnabled(True)
            self.sDefault.setMaximum(1)
            self.sEscape.setMaximum(1)

    def on_cButton2_editTextChanged(self, text):
        """
        Private slot to enable/disable the other button combos depending on its contents.
        
        @param text the new text (QString)
        """
        if text.isEmpty():
            self.sDefault.setMaximum(1)
            self.sEscape.setMaximum(1)
        else:
            self.sDefault.setMaximum(2)
            self.sEscape.setMaximum(2)

    def __enabledGroups(self):
        """
        Private method to enable/disable some group boxes.
        """
        self.buttons.setEnabled(not self.rQt42.isChecked() and \
                                not self.rAbout.isChecked() and \
                                not self.rAboutQt.isChecked()
        )
        self.standardButtons.setEnabled(self.rQt42.isChecked() and \
                                        not self.rAbout.isChecked() and \
                                        not self.rAboutQt.isChecked()
        )
    
    def on_rQt42_toggled(self, on):
        """
        Private slot to handle the toggled signal of the rQt42 radio button.
        
        @param on toggle state (boolean) (ignored)
        """
        self.__enabledGroups()
    
    def on_rAbout_toggled(self, on):
        """
        Private slot to handle the toggled signal of the rAbout radio button.
        
        @param on toggle state (boolean) (ignored)
        """
        self.__enabledGroups()
    
    def on_rAboutQt_toggled(self, on):
        """
        Private slot to handle the toggled signal of the rAboutQt radio button.
        
        @param on toggle state (boolean) (ignored)
        """
        self.__enabledGroups()
    
    def __getQt40ButtonCode(self, istring):
        """
        Private method to generate the button code for Qt3 and Qt 4.0.
        
        @param istring indentation string (string)
        @return the button code (string)
        """
        btnCode = ""
        b1 = None
        b2 = None
        b3 = None
        if not self.cButton0.currentText().isEmpty():
            b1 = self.cButton0.currentText()
            if not self.cButton1.currentText().isEmpty():
                b2 = self.cButton1.currentText()
                if not self.cButton2.currentText().isEmpty():
                    b3 = self.cButton2.currentText()
        for button in [b1, b2, b3]:
            if button is None:
                btnCode += ',%s%sQString()' % (os.linesep, istring)
            else:
                btnCode += ',%s%sself.trUtf8("%s")' % \
                    (os.linesep, istring, unicode(button))
        btnCode += ',%s%s%d, %d' % \
            (os.linesep, istring, self.sDefault.value(), self.sEscape.value())
        return btnCode
    
    def __getQt42ButtonCode(self, istring, indString):
        """
        Private method to generate the button code for Qt 4.2.0.
        
        @param istring indentation string (string)
        @param indString string used for indentation (space or tab) (string)
        @return the button code (string)
        """
        buttons = []
        if self.abortCheck.isChecked():
            buttons.append("QMessageBox.Abort")
        if self.applyCheck.isChecked():
            buttons.append("QMessageBox.Apply")
        if self.cancelCheck.isChecked():
            buttons.append("QMessageBox.Cancel")
        if self.closeCheck.isChecked():
            buttons.append("QMessageBox.Close")
        if self.discardCheck.isChecked():
            buttons.append("QMessageBox.Discard")
        if self.helpCheck.isChecked():
            buttons.append("QMessageBox.Help")
        if self.ignoreCheck.isChecked():
            buttons.append("QMessageBox.Ignore")
        if self.noCheck.isChecked():
            buttons.append("QMessageBox.No")
        if self.notoallCheck.isChecked():
            buttons.append("QMessageBox.NoToAll")
        if self.okCheck.isChecked():
            buttons.append("QMessageBox.Ok")
        if self.openCheck.isChecked():
            buttons.append("QMessageBox.Open")
        if self.resetCheck.isChecked():
            buttons.append("QMessageBox.Reset")
        if self.restoreCheck.isChecked():
            buttons.append("QMessageBox.RestoreDefaults")
        if self.retryCheck.isChecked():
            buttons.append("QMessageBox.Retry")
        if self.saveCheck.isChecked():
            buttons.append("QMessageBox.Save")
        if self.saveallCheck.isChecked():
            buttons.append("QMessageBox.SaveAll")
        if self.yesCheck.isChecked():
            buttons.append("QMessageBox.Yes")
        if self.yestoallCheck.isChecked():
            buttons.append("QMessageBox.YesToAll")
        if len(buttons) == 0:
            return ""
        
        istring2 = istring + indString
        joinstring = ' | \\%s%s' % (os.linesep, istring2)
        btnCode = ',%s%sQMessageBox.StandardButtons(\\' % (os.linesep, istring)
        btnCode += '%s%s%s)' % (os.linesep, istring2, joinstring.join(buttons))
        defaultIndex = self.defaultCombo.currentIndex()
        if defaultIndex:
            btnCode += ',%s%s%s' % (os.linesep, istring, 
                self.buttonsCodeListText[defaultIndex])
        return btnCode
    
    def getCode(self, indLevel, indString):
        """
        Public method to get the source code.
        
        @param indLevel indentation level (int)
        @param indString string used for indentation (space or tab) (string)
        @return generated code (string)
        """
        # calculate our indentation level and the indentation string
        il = indLevel + 1
        istring = il * indString
        
        # now generate the code
        msgdlg = 'QMessageBox.'
        if self.rAbout.isChecked():
            msgdlg += "about(None,%s" % os.linesep
        elif self.rAboutQt.isChecked():
            msgdlg += "aboutQt(None, %s" % os.linesep
        elif self.rInformation.isChecked():
            msgdlg += "information(None,%s" % os.linesep
        elif self.rQuestion.isChecked():
            msgdlg += "question(None,%s" % os.linesep
        elif self.rWarning.isChecked():
            msgdlg += "warning(None,%s" % os.linesep
        else:
            msgdlg +="critical(None,%s" % os.linesep
        msgdlg += '%sself.trUtf8("%s")' % (istring, unicode(self.eCaption.text()))
        if not self.rAboutQt.isChecked():
            msgdlg += ',%s%sself.trUtf8("""%s""")' % \
                (os.linesep, istring, unicode(self.eMessage.toPlainText()))
        if not self.rAbout.isChecked() and not self.rAboutQt.isChecked():
            if self.rQt42.isChecked():
                msgdlg += self.__getQt42ButtonCode(istring, indString)
            else:
                msgdlg += self.__getQt40ButtonCode(istring)
        msgdlg +=')%s' % os.linesep
        return msgdlg
