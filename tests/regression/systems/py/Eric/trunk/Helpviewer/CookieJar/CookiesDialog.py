# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show all cookies.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from CookieModel import CookieModel
from CookieDetailsDialog import CookieDetailsDialog
from CookiesExceptionsDialog import CookiesExceptionsDialog

from Ui_CookiesDialog import Ui_CookiesDialog

import UI.PixmapCache

class CookiesDialog(QDialog, Ui_CookiesDialog):
    """
    Class implementing a dialog to show all cookies.
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
        self.addButton.setEnabled(False)
        
        self.__cookieJar = cookieJar
        
        self.connect(self.removeButton, SIGNAL("clicked()"), 
                     self.cookiesTable.removeSelected)
        self.connect(self.removeAllButton, SIGNAL("clicked()"), 
                     self.cookiesTable.removeAll)
        
        self.cookiesTable.verticalHeader().hide()
        model = CookieModel(cookieJar, self)
        self.__proxyModel = QSortFilterProxyModel(self)
        self.__proxyModel.setSourceModel(model)
        self.connect(self.searchEdit, SIGNAL("textChanged(QString)"), 
                     self.__proxyModel.setFilterFixedString)
        self.cookiesTable.setModel(self.__proxyModel)
        self.connect(self.cookiesTable, 
                     SIGNAL("doubleClicked(const QModelIndex&)"), 
                     self.__showCookieDetails)
        self.connect(self.cookiesTable.selectionModel(), 
                     SIGNAL("selectionChanged(const QItemSelection&, const QItemSelection&)"), 
                     self.__tableSelectionChanged)
        self.connect(self.cookiesTable.model(), 
                     SIGNAL("modelReset()"), 
                     self.__tableModelReset)
        
        fm = QFontMetrics(QFont())
        height = fm.height() + fm.height() / 3
        self.cookiesTable.verticalHeader().setDefaultSectionSize(height)
        self.cookiesTable.verticalHeader().setMinimumSectionSize(-1)
        for section in range(model.columnCount()):
            header = self.cookiesTable.horizontalHeader().sectionSizeHint(section)
            if section == 0:
                header = fm.width("averagebiglonghost.averagedomain.info")
            elif section == 1:
                header = fm.width("_session_id")
            elif section == 4:
                header = fm.width(QDateTime.currentDateTime().toString(Qt.LocalDate))
            buffer = fm.width("mm")
            header += buffer
            self.cookiesTable.horizontalHeader().resizeSection(section, header)
        self.cookiesTable.horizontalHeader().setStretchLastSection(True)
        
        self.__detailsDialog = None
    
    def __showCookieDetails(self, index):
        """
        Private slot to show a dialog with the cookie details.
        
        @param index index of the entry to show (QModelIndex)
        """
        if not index.isValid():
            return
        
        cookiesTable = self.sender()
        if cookiesTable is None:
            return
        
        model = cookiesTable.model()
        row = index.row()
        
        domain = model.data(model.index(row, 0)).toString()
        name = model.data(model.index(row, 1)).toString()
        path = model.data(model.index(row, 2)).toString()
        secure = model.data(model.index(row, 3)).toBool()
        expires = model.data(model.index(row, 4)).toDateTime()\
            .toString("yyyy-MM-dd hh:mm")
        value = QString(
            QByteArray.fromPercentEncoding(model.data(model.index(row, 5)).toByteArray()))
        
        if self.__detailsDialog is None:
            self.__detailsDialog = CookieDetailsDialog(self)
        self.__detailsDialog.setData(domain, name, path, secure, expires, value)
        self.__detailsDialog.show()
    
    @pyqtSignature("")
    def on_addButton_clicked(self):
        """
        Private slot to add a new exception.
        """
        selection = self.cookiesTable.selectionModel().selectedRows()
        if len(selection) == 0:
            return
        
        firstSelected = selection[0]
        domainSelection = firstSelected.sibling(firstSelected.row(), 0)
        domain = self.__proxyModel.data(domainSelection, Qt.DisplayRole).toString()
        dlg = CookiesExceptionsDialog(self.__cookieJar, self)
        dlg.setDomainName(domain)
        dlg.exec_()
    
    def __tableSelectionChanged(self, selected, deselected):
        """
        Private slot to handle a change of selected items.
        
        @param selected selected indexes (QItemSelection)
        @param deselected deselected indexes (QItemSelection)
        """
        self.addButton.setEnabled(len(selected.indexes()) > 0)
    
    def __tableModelReset(self):
        """
        Private slot to handle a reset of the cookies table.
        """
        self.addButton.setEnabled(False)
