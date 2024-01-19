# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog for the configuration of cookie exceptions.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from CookieJar import CookieJar
from CookieExceptionsModel import CookieExceptionsModel
from CookieModel import CookieModel

from Ui_CookiesExceptionsDialog import Ui_CookiesExceptionsDialog

import UI.PixmapCache

class CookiesExceptionsDialog(QDialog, Ui_CookiesExceptionsDialog):
    """
    Class implementing a dialog for the configuration of cookie exceptions.
    """
    def __init__(self, cookieJar, parent = None):
        """
        Constructor
        
        @param cookieJar reference to the cookie jar (CookieJar)
        @param parent reference to the parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.clearButton.setIcon(UI.PixmapCache.getIcon("clearLeft.png"))
        
        self.__cookieJar = cookieJar
        
        self.connect(self.removeButton, SIGNAL("clicked()"), 
                     self.exceptionsTable.removeSelected)
        self.connect(self.removeAllButton, SIGNAL("clicked()"), 
                     self.exceptionsTable.removeAll)
        
        self.exceptionsTable.verticalHeader().hide()
        self.__exceptionsModel = CookieExceptionsModel(cookieJar)
        self.__proxyModel = QSortFilterProxyModel(self)
        self.__proxyModel.setSourceModel(self.__exceptionsModel)
        self.connect(self.searchEdit, SIGNAL("textChanged(QString)"), 
                     self.__proxyModel.setFilterFixedString)
        self.exceptionsTable.setModel(self.__proxyModel)
        
        cookieModel = CookieModel(cookieJar, self)
        self.domainEdit.setCompleter(QCompleter(cookieModel, self.domainEdit))
        
        f = QFont()
        f.setPointSize(10)
        fm = QFontMetrics(f)
        height = fm.height() + fm.height() / 3
        self.exceptionsTable.verticalHeader().setDefaultSectionSize(height)
        self.exceptionsTable.verticalHeader().setMinimumSectionSize(-1)
        for section in range(self.__exceptionsModel.columnCount()):
            header = self.exceptionsTable.horizontalHeader().sectionSizeHint(section)
            if section == 0:
                header = fm.width("averagebiglonghost.averagedomain.info")
            elif section == 1:
                header = fm.width(self.trUtf8("Allow For Session"))
            buffer = fm.width("mm")
            header += buffer
            self.exceptionsTable.horizontalHeader().resizeSection(section, header)
    
    def setDomainName(self, domain):
        """
        Public method to set the domain to be displayed.
        
        @param domain domain name to be displayed (string or QString)
        """
        self.domainEdit.setText(domain)
    
    @pyqtSignature("QString")
    def on_domainEdit_textChanged(self, txt):
        """
        Private slot to handle a change of the domain edit text.
        
        @param txt current text of the edit (QString)
        """
        enabled = not txt.isEmpty()
        self.blockButton.setEnabled(enabled)
        self.allowButton.setEnabled(enabled)
        self.allowForSessionButton.setEnabled(enabled)
    
    @pyqtSignature("")
    def on_blockButton_clicked(self):
        """
        Private slot to block cookies of a domain.
        """
        self.__exceptionsModel.addRule(self.domainEdit.text(), CookieJar.Block)
    
    @pyqtSignature("")
    def on_allowForSessionButton_clicked(self):
        """
        Private slot to allow cookies of a domain for the current session only.
        """
        self.__exceptionsModel.addRule(self.domainEdit.text(), CookieJar.AllowForSession)
    
    @pyqtSignature("")
    def on_allowButton_clicked(self):
        """
        Private slot to allow cookies of a domain.
        """
        self.__exceptionsModel.addRule(self.domainEdit.text(), CookieJar.Allow)
