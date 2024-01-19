# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the cookies configuration dialog.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from CookiesDialog import CookiesDialog
from CookiesExceptionsDialog import CookiesExceptionsDialog
from CookieJar import CookieJar

from Ui_CookiesConfigurationDialog import Ui_CookiesConfigurationDialog

import Preferences

class CookiesConfigurationDialog(QDialog, Ui_CookiesConfigurationDialog):
    """
    Class implementing the cookies configuration dialog.
    """
    def __init__(self, parent):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.__mw = parent
        
        jar = self.__mw.cookieJar()
        acceptPolicy = jar.acceptPolicy()
        if acceptPolicy == CookieJar.AcceptAlways:
            self.acceptCombo.setCurrentIndex(0)
        elif acceptPolicy == CookieJar.AcceptNever:
            self.acceptCombo.setCurrentIndex(1)
        elif acceptPolicy == CookieJar.AcceptOnlyFromSitesNavigatedTo:
            self.acceptCombo.setCurrentIndex(2)
        
        keepPolicy = jar.keepPolicy()
        if keepPolicy == CookieJar.KeepUntilExpire:
            self.keepUntilCombo.setCurrentIndex(0)
        elif keepPolicy == CookieJar.KeepUntilExit:
            self.keepUntilCombo.setCurrentIndex(1)
        elif keepPolicy == CookieJar.KeepUntilTimeLimit:
            self.keepUntilCombo.setCurrentIndex(2)
        
        self.filterTrackingCookiesCheckbox.setChecked(jar.filterTrackingCookies())
    
    def accept(self):
        """
        Public slot to accept the dialog.
        """
        acceptSelection = self.acceptCombo.currentIndex()
        if acceptSelection == 0:
            acceptPolicy = CookieJar.AcceptAlways
        elif acceptSelection == 1:
            acceptPolicy = CookieJar.AcceptNever
        elif acceptSelection == 2:
            acceptPolicy = CookieJar.AcceptOnlyFromSitesNavigatedTo
        
        keepSelection = self.keepUntilCombo.currentIndex()
        if keepSelection == 0:
            keepPolicy = CookieJar.KeepUntilExpire
        elif keepSelection == 1:
            keepPolicy = CookieJar.KeepUntilExit
        elif keepSelection == 2:
            keepPolicy = CookieJar.KeepUntilTimeLimit
        
        jar = self.__mw.cookieJar()
        jar.setAcceptPolicy(acceptPolicy)
        jar.setKeepPolicy(keepPolicy)
        jar.setFilterTrackingCookies(self.filterTrackingCookiesCheckbox.isChecked())
        
        QDialog.accept(self)
    
    @pyqtSignature("")
    def on_exceptionsButton_clicked(self):
        """
        Private slot to show the cookies exceptions dialog.
        """
        dlg = CookiesExceptionsDialog(self.__mw.cookieJar())
        dlg.exec_()
    
    @pyqtSignature("")
    def on_cookiesButton_clicked(self):
        """
        Private slot to show the cookies dialog.
        """
        dlg = CookiesDialog(self.__mw.cookieJar())
        dlg.exec_()
