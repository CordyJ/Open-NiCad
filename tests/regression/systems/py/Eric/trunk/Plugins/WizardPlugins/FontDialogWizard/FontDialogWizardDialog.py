# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the font dialog wizard dialog.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_FontDialogWizardDialog import Ui_FontDialogWizardDialog

class FontDialogWizardDialog(QDialog, Ui_FontDialogWizardDialog):
    """
    Class implementing the font dialog wizard dialog.
    
    It displays a dialog for entering the parameters
    for the QFontDialog code generator.
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
        
        self.font = None
        
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
        if self.font is None:
            QFontDialog.getFont()
        else:
            QFontDialog.getFont(self.font)
        
    def on_eVariable_textChanged(self, text):
        """
        Private slot to handle the textChanged signal of eVariable.
        
        @param text the new text (QString)
        """
        if text.isEmpty():
            self.bTest.setEnabled(True)
        else:
            self.bTest.setEnabled(False)
        
    @pyqtSignature("")
    def on_fontButton_clicked(self):
        """
        Private slot to handle the button press to select a font via a font selection 
        dialog.
        """
        if self.font is None:
            font, ok = QFontDialog.getFont()
        else:
            font, ok = QFontDialog.getFont(self.font)
        if ok:
            self.font = font
        else:
            self.font = None
        
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
        code = 'QFontDialog.getFont('
        if self.eVariable.text().isEmpty():
            if self.font is not None:
                code += 'QFont("%s", %d, %d, %d)' % \
                    (self.font.family(), self.font.pointSize(),
                    self.font.weight(), self.font.italic())
        else:
            code += str(self.eVariable.text())
        code += ')%s' % os.linesep
            
        return code
