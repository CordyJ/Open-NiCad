# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the connection parameters.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import QSqlDatabase

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4FileCompleter

from Ui_SqlConnectionDialog import Ui_SqlConnectionDialog

import Utilities

class SqlConnectionDialog(QDialog, Ui_SqlConnectionDialog):
    """
    Class implementing a dialog to enter the connection parameters.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.databaseFileCompleter = E4FileCompleter()
        
        self.okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        
        drivers = QSqlDatabase.drivers()
        
        # remove compatibility names
        drivers.removeAll("QMYSQL3")
        drivers.removeAll("QOCI8")
        drivers.removeAll("QODBC3")
        drivers.removeAll("QPSQL7")
        drivers.removeAll("QTDS7")
        
        self.driverCombo.addItems(drivers)
        
        self.__updateDialog()
    
    def __updateDialog(self):
        """
        Private slot to update the dialog depending on it's contents.
        """
        driver = self.driverCombo.currentText()
        if driver.startsWith("QSQLITE"):
            self.databaseEdit.setCompleter(self.databaseFileCompleter)
            self.databaseFileButton.setEnabled(True)
        else:
            self.databaseEdit.setCompleter(None)
            self.databaseFileButton.setEnabled(False)
        
        if self.databaseEdit.text().isEmpty() or driver.isEmpty():
            self.okButton.setEnabled(False)
        else:
            self.okButton.setEnabled(True)
    
    @pyqtSignature("QString")
    def on_driverCombo_activated(self, txt):
        """
        Private slot handling the selection of a database driver.
        """
        self.__updateDialog()
    
    @pyqtSignature("QString")
    def on_databaseEdit_textChanged(self, p0):
        """
        Private slot handling the change of the database name.
        """
        self.__updateDialog()
    
    @pyqtSignature("")
    def on_databaseFileButton_clicked(self):
        """
        Private slot to open a database file via a file selection dialog.
        """
        startdir = self.databaseEdit.text()
        dbFile = KQFileDialog.getOpenFileName(
            self,
            self.trUtf8("Select Database File"),
            startdir,
            self.trUtf8("All Files (*)"),
            None)
        
        if not dbFile.isEmpty():
            self.databaseEdit.setText(Utilities.toNativeSeparators(dbFile))
    
    def getData(self):
        """
        Public method to retrieve the connection data.
        
        @return tuple giving the driver name (QString), the database name (QString),
            the user name (QString), the password (QString), the host name (QString)
            and the port (integer)
        """
        return (
            self.driverCombo.currentText(), 
            self.databaseEdit.text(), 
            self.usernameEdit.text(), 
            self.passwordEdit.text(), 
            self.hostnameEdit.text(), 
            self.portSpinBox.value(), 
        )
