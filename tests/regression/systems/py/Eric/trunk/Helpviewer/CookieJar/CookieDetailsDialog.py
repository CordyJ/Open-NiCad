# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog showing the cookie data.
"""

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature

from Ui_CookieDetailsDialog import Ui_CookieDetailsDialog

class CookieDetailsDialog(QDialog, Ui_CookieDetailsDialog):
    """
    Class implementing a dialog showing the cookie data.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
    
    def setData(self, domain, name, path, secure, expires, value):
        """
        Public method to set the data to be shown.
        
        @param domain domain of the cookie (QString)
        @param name name of the cookie (QString)
        @param path path of the cookie (QString)
        @param secure flag indicating a secure cookie (boolean)
        @param expires expiration time of the cookie (QString)
        @param value value of the cookie (QString)
        """
        self.domainEdit.setText(domain)
        self.nameEdit.setText(name)
        self.pathEdit.setText(path)
        self.secureCheckBox.setChecked(secure)
        self.expirationEdit.setText(expires)
        self.valueEdit.setPlainText(value)
