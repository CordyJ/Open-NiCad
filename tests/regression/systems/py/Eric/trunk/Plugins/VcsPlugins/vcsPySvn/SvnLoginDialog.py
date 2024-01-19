# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the login dialog for pysvn.
"""

from PyQt4.QtGui import QDialog

from Ui_SvnLoginDialog import Ui_SvnLoginDialog

class SvnLoginDialog(QDialog, Ui_SvnLoginDialog):
    """
    Class implementing the login dialog for pysvn.
    """
    def __init__(self, realm, username, may_save, parent = None):
        """
        Constructor
        
        @param realm name of the realm of the requested credentials (string)
        @param username username as supplied by subversion (string)
        @param may_save flag indicating, that subversion is willing to save
            the answers returned (boolean)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.realmLabel.setText(self.trUtf8("<b>Enter login data for realm %1.</b>")\
                                .arg(realm))
        self.usernameEdit.setText(username)
        self.saveCheckBox.setEnabled(may_save)
        if not may_save:
            self.saveCheckBox.setChecked(False)
        
    def getData(self):
        """
        Public method to retrieve the login data.
        
        @return tuple of three values (username, password, save)
        """
        return (str(self.usernameEdit.text()),
               str(self.passwordEdit.text()),
               self.saveCheckBox.isChecked())
