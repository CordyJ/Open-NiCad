# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Email configuration page.
"""

from PyQt4.QtGui import QIntValidator

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EmailPage import Ui_EmailPage

import Preferences

class EmailPage(ConfigurationPageBase, Ui_EmailPage):
    """
    Class implementing the Email configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EmailPage")
        
        self.portValidator = QIntValidator(1, 65535, self.portEdit)
        self.portEdit.setValidator(self.portValidator)
        
        # set initial values
        self.mailServerEdit.setText(Preferences.getUser("MailServer"))
        self.portEdit.setText("%d" % Preferences.getUser("MailServerPort"))
        self.emailEdit.setText(Preferences.getUser("Email"))
        self.signatureEdit.setPlainText(Preferences.getUser("Signature"))
        self.mailAuthenticationCheckBox.setChecked(\
            Preferences.getUser("MailServerAuthentication"))
        self.mailUserEdit.setText(Preferences.getUser("MailServerUser"))
        self.mailPasswordEdit.setText(\
            Preferences.getUser("MailServerPassword"))
        self.useTlsCheckBox.setChecked(\
            Preferences.getUser("MailServerUseTLS"))
        
    def save(self):
        """
        Public slot to save the Email configuration.
        """
        Preferences.setUser("MailServer",
            self.mailServerEdit.text())
        Preferences.setUser("MailServerPort", 
            int(self.portEdit.text()))
        Preferences.setUser("Email",
            self.emailEdit.text())
        Preferences.setUser("Signature",
            self.signatureEdit.toPlainText())
        Preferences.setUser("MailServerAuthentication",
            int(self.mailAuthenticationCheckBox.isChecked()))
        Preferences.setUser("MailServerUser",
            self.mailUserEdit.text())
        Preferences.setUser("MailServerPassword",
            self.mailPasswordEdit.text())
        Preferences.setUser("MailServerUseTLS",
            int(self.useTlsCheckBox.isChecked()))
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EmailPage()
    return page
