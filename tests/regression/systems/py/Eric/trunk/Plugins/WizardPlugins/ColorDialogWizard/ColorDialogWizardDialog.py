# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the color dialog wizard dialog.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox

from Ui_ColorDialogWizardDialog import Ui_ColorDialogWizardDialog

class ColorDialogWizardDialog(QDialog, Ui_ColorDialogWizardDialog):
    """
    Class implementing the color dialog wizard dialog.
    
    It displays a dialog for entering the parameters
    for the QColorDialog code generator.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.bTest = \
            self.buttonBox.addButton(self.trUtf8("Test"), QDialogButtonBox.ActionRole)
        
        if qVersion() < "4.5.0":
            self.rQt40.setChecked(True)
        else:
            self.rQt45.setChecked(True)
    
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
        if self.rColor.isChecked():
            if self.eColor.currentText().isEmpty():
                QColorDialog.getColor()
            else:
                coStr = unicode(self.eColor.currentText())
                if coStr.startswith('#'):
                    coStr = "QColor('%s')" % coStr
                else:
                    coStr = "QColor(%s)" % coStr
                try:
                    if self.rQt45.isChecked():
                        exec 'QColorDialog.getColor(%s, None, "%s")' % \
                            (coStr, self.eTitle.text())
                    else:
                        exec 'QColorDialog.getColor(%s)' % coStr
                except:
                    KQMessageBox.critical(None,
                        self.trUtf8("QColorDialog Wizard Error"),
                        self.trUtf8("""<p>The colour <b>%1</b> is not valid.</p>""")
                            .arg(coStr))
            
        elif self.rRGBA.isChecked():
            if self.rQt45.isChecked():
                QColorDialog.getColor(
                    QColor(self.sRed.value(), self.sGreen.value(),
                           self.sBlue.value(), self.sAlpha.value()), 
                    None, self.eTitle.text(), 
                    QColorDialog.ColorDialogOptions(QColorDialog.ShowAlphaChannel))
            else:
                rgba = qRgba(self.sRed.value(), self.sGreen.value(),
                    self.sBlue.value(), self.sAlpha.value())
                QColorDialog.getRgba(rgba)
        
    def on_eRGB_textChanged(self, text):
        """
        Private slot to handle the textChanged signal of eRGB.
        
        @param text the new text (QString)
        """
        if text.isEmpty():
            self.sRed.setEnabled(True)
            self.sGreen.setEnabled(True)
            self.sBlue.setEnabled(True)
            self.sAlpha.setEnabled(True)
            self.bTest.setEnabled(True)
        else:
            self.sRed.setEnabled(False)
            self.sGreen.setEnabled(False)
            self.sBlue.setEnabled(False)
            self.sAlpha.setEnabled(False)
            self.bTest.setEnabled(False)

    def on_eColor_editTextChanged(self, text):
        """
        Private slot to handle the editTextChanged signal of eColor.
        
        @param text the new text (QString)
        """
        if text.isEmpty() or text.startsWith('Qt.') or text.startsWith('#'):
            self.bTest.setEnabled(True)
        else:
            self.bTest.setEnabled(False)
    
    def on_rQt45_toggled(self, on):
        """
        Private slot to handle the toggled signal of the rQt45 radio button.
        
        @param on toggle state (boolean) (ignored)
        """
        self.titleGroup.setEnabled(on)
    
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
        code = 'QColorDialog.'
        if self.rColor.isChecked():
            code += 'getColor('
            if not self.eColor.currentText().isEmpty():
                col = str(self.eColor.currentText())
                if col.startswith('#'):
                    code += 'QColor("%s")' % col
                else:
                    code += 'QColor(%s)' % col
            if self.rQt45.isChecked():
                code += ', None,%s' % os.linesep
                code += '%sself.trUtf8("%s"),%s' % \
                    (istring, self.eTitle.text(), os.linesep)
                code += \
                    '%sQColorDialog.ColorDialogOptions(QColorDialog.ShowAlphaChannel)' % \
                        istring
            code += ')%s' % os.linesep
        elif self.rRGBA.isChecked():
            if self.rQt45.isChecked():
                code += 'getColor('
                if self.eRGB.text().isEmpty():
                    code += 'QColor(%d, %d, %d, %d),%s' % \
                        (self.sRed.value(), self.sGreen.value(), self.sBlue.value(),
                        self.sAlpha.value(), os.linesep)
                else:
                    code += '%s,%s' % (self.eRGB.text(), os.linesep)
                code += '%sNone,%s' % (istring, os.linesep)
                code += '%sself.trUtf8("%s"),%s' % \
                    (istring, self.eTitle.text(), os.linesep)
                code += \
                    '%sQColorDialog.ColorDialogOptions(QColorDialog.ShowAlphaChannel)' % \
                        istring
                code += ')%s' % os.linesep
            else:
                code += 'getRgba('
                if self.eRGB.text().isEmpty():
                    code += 'qRgba(%d, %d, %d, %d)' % \
                        (self.sRed.value(), self.sGreen.value(), self.sBlue.value(),
                        self.sAlpha.value())
                else:
                    code += str(self.eRGB.text())
                code += ')%s' % os.linesep
            
        return code
