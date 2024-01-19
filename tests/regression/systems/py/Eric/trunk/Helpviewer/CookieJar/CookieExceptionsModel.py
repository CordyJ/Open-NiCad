# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the cookie exceptions model.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from CookieJar import CookieJar

class CookieExceptionsModel(QAbstractTableModel):
    """
    Class implementing the cookie exceptions model.
    """
    def __init__(self, cookieJar, parent = None):
        """
        Constructor
        
        @param cookieJar reference to the cookie jar (CookieJar)
        @param parent reference to the parent object (QObject)
        """
        QAbstractTableModel.__init__(self, parent)
        
        self.__cookieJar = cookieJar
        self.__allowedCookies = self.__cookieJar.allowedCookies()
        self.__blockedCookies = self.__cookieJar.blockedCookies()
        self.__sessionCookies = self.__cookieJar.allowForSessionCookies()
        
        self.__headers = [
            self.trUtf8("Website"), 
            self.trUtf8("Status"), 
        ]
    
    def headerData(self, section, orientation, role):
        """
        Public method to get header data from the model.
        
        @param section section number (integer)
        @param orientation orientation (Qt.Orientation)
        @param role role of the data to retrieve (integer)
        @return requested data
        """
        if role == Qt.SizeHintRole:
            fm = QFontMetrics(QFont())
            height = fm.height() + fm.height() / 3
            width = \
                fm.width(self.headerData(section, orientation, Qt.DisplayRole).toString())
            return QVariant(QSize(width, height))
        
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return QVariant(self.__headers[section])
            except IndexError:
                return QVariant()
        
        return QAbstractTableModel.headerData(self, section, orientation, role)
    
    def data(self, index, role):
        """
        Public method to get data from the model.
        
        @param index index to get data for (QModelIndex)
        @param role role of the data to retrieve (integer)
        @return requested data
        """
        if index.row() < 0 or index.row() >= self.rowCount():
            return QVariant()
        
        if role in (Qt.DisplayRole, Qt.EditRole):
            row = index.row()
            if row < len(self.__allowedCookies):
                if index.column() == 0:
                    return QVariant(self.__allowedCookies[row])
                elif index.column() == 1:
                    return QVariant(self.trUtf8("Allow"))
                else:
                    return QVariant()
            
            row -= len(self.__allowedCookies)
            if row < len(self.__blockedCookies):
                if index.column() == 0:
                    return QVariant(self.__blockedCookies[row])
                elif index.column() == 1:
                    return QVariant(self.trUtf8("Block"))
                else:
                    return QVariant()
            
            row -= len(self.__blockedCookies)
            if row < len(self.__sessionCookies):
                if index.column() == 0:
                    return QVariant(self.__sessionCookies[row])
                elif index.column() == 1:
                    return QVariant(self.trUtf8("Allow For Session"))
                else:
                    return QVariant()
            
            return QVariant()
        
        return QVariant()
    
    def columnCount(self, parent = QModelIndex()):
        """
        Public method to get the number of columns of the model.
        
        @param parent parent index (QModelIndex)
        @return number of columns (integer)
        """
        if parent.isValid():
            return 0
        else:
            return len(self.__headers)
    
    def rowCount(self, parent = QModelIndex()):
        """
        Public method to get the number of rows of the model.
        
        @param parent parent index (QModelIndex)
        @return number of columns (integer)
        """
        if parent.isValid() or self.__cookieJar is None:
            return 0
        else:
            return len(self.__allowedCookies) + \
                   len(self.__blockedCookies) + \
                   len(self.__sessionCookies)
    
    def removeRows(self, row, count, parent = QModelIndex()):
        """
        Public method to remove entries from the model.
        
        @param row start row (integer)
        @param count number of rows to remove (integer)
        @param parent parent index (QModelIndex)
        @return flag indicating success (boolean)
        """
        if parent.isValid() or self.__cookieJar is None:
            return False
        
        lastRow = row + count - 1
        self.beginRemoveRows(parent, row, lastRow)
        for i in range(lastRow, row - 1, -1):
            rowToRemove = i
            
            if rowToRemove < len(self.__allowedCookies):
                del self.__allowedCookies[rowToRemove]
                continue
            
            rowToRemove -= len(self.__allowedCookies)
            if rowToRemove < len(self.__blockedCookies):
                del self.__blockedCookies[rowToRemove]
                continue
            
            rowToRemove -= len(self.__blockedCookies)
            if rowToRemove < len(self.__sessionCookies):
                del self.__sessionCookies[rowToRemove]
                continue
        
        self.__cookieJar.setAllowedCookies(self.__allowedCookies)
        self.__cookieJar.setBlockedCookies(self.__blockedCookies)
        self.__cookieJar.setAllowForSessionCookies(self.__sessionCookies)
        self.endRemoveRows()
        
        return True
    
    def addRule(self, host, rule):
        """
        Public method to add an exception rule.
        
        @param host name of the host to add a rule for (QString)
        @param rule type of rule to add (CookieJar.Allow, CookieJar.Block or
            CookieJar.AllowForSession)
        """
        if host.isEmpty():
            return
        
        if rule == CookieJar.Allow:
            self.__addHost(host, 
                self.__allowedCookies, self.__blockedCookies, self.__sessionCookies)
            return
        elif rule == CookieJar.Block:
            self.__addHost(host, 
                self.__blockedCookies, self.__allowedCookies, self.__sessionCookies)
            return
        elif rule == CookieJar.AllowForSession:
            self.__addHost(host, 
                self.__sessionCookies, self.__allowedCookies, self.__blockedCookies)
            return
    
    def __addHost(self, host, addList, removeList1, removeList2):
        """
        Private method to add a host to an exception list.
        
        @param host name of the host to add (QString)
        @param addList reference to the list to add it to (QStringList)
        @param removeList1 reference to first list to remove it from (QStringList)
        @param removeList2 reference to second list to remove it from (QStringList)
        """
        if not addList.contains(host):
            addList.append(host)
            removeList1.removeOne(host)
            removeList2.removeOne(host)
        
        # Avoid to have similar rules (with or without leading dot)
        # e.g. python-projects.org and .python-projects.org
        if host.startsWith("."):
            otherRule = host[1:]
        else:
            otherRule = '.' + host
        addList.removeOne(otherRule)
        removeList1.removeOne(otherRule)
        removeList2.removeOne(otherRule)
        
        self.reset()
