# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the data for a new property.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4FileCompleter

from Ui_SvnPropSetDialog import Ui_SvnPropSetDialog

import Utilities

class SvnPropSetDialog(QDialog, Ui_SvnPropSetDialog):
    """
    Class implementing a dialog to enter the data for a new property.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.propFileCompleter = E4FileCompleter(self.propFileEdit)
        
    @pyqtSignature("")
    def on_fileButton_clicked(self):
        """
        Private slot called by pressing the file selection button.
        """
        fn = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select file for property"),
            self.propFileEdit.text(),
            QString())
        
        if not fn.isEmpty():
            self.propFileEdit.setText(Utilities.toNativeSeparators(fn))
        
    def getData(self):
        """
        Public slot used to retrieve the data entered into the dialog.
        
        @return tuple of three values giving the property name, a flag
            indicating a file was selected and the text of the property
            or the selected filename. (QString, boolean, QString)
        """
        if self.fileRadioButton.isChecked():
            return (self.propNameEdit.text(), True, self.propFileEdit.text())
        else:
            return (self.propNameEdit.text(), False, self.propTextEdit.toPlainText())
