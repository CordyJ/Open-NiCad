# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a network monitor dialog.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtNetwork import QNetworkRequest, QNetworkAccessManager

import UI.PixmapCache

from E4NetworkHeaderDetailsDialog import E4NetworkHeaderDetailsDialog

from Ui_E4NetworkMonitor import Ui_E4NetworkMonitor

class E4NetworkRequest(object):
    """
    Class for storing all data related to a specific request.
    """
    def __init__(self):
        """
        Constructor
        """
        self.op = -1
        self.request = None
        self.reply = None
        
        self.response = ""
        self.length = 0
        self.contentType = ""
        self.info = ""
        self.replyHeaders = []  # list of tuple of two items

class E4NetworkMonitor(QDialog, Ui_E4NetworkMonitor):
    """
    Class implementing a network monitor dialog.
    """
    _monitor = None
    
    @classmethod
    def instance(cls, networkAccessManager):
        """
        Class method to get a reference to our singleton.
        
        @param networkAccessManager reference to the network access manager
            (QNetworkAccessManager)
        """
        if cls._monitor is None:
            cls._monitor = E4NetworkMonitor(networkAccessManager)
            cls._monitor.setAttribute(Qt.WA_DeleteOnClose, True)
        
        return cls._monitor
    
    @classmethod
    def closeMonitor(cls):
        """
        Class method to close the monitor dialog.
        """
        if cls._monitor is not None:
            cls._monitor.close()
    
    def __init__(self, networkAccessManager, parent = None):
        """
        Constructor
        
        @param networkAccessManager reference to the network access manager
            (QNetworkAccessManager)
        @param parent reference to the parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.clearButton.setIcon(UI.PixmapCache.getIcon("clearLeft.png"))
        
        self.__requestHeaders = QStandardItemModel(self)
        self.__requestHeaders.setHorizontalHeaderLabels(
            [self.trUtf8("Name"), self.trUtf8("Value")])
        self.requestHeadersList.setModel(self.__requestHeaders)
        self.requestHeadersList.horizontalHeader().setStretchLastSection(True)
        self.connect(self.requestHeadersList, 
                     SIGNAL("doubleClicked(const QModelIndex&)"), 
                     self.__showHeaderDetails)
        
        self.__replyHeaders = QStandardItemModel(self)
        self.__replyHeaders.setHorizontalHeaderLabels(
            [self.trUtf8("Name"), self.trUtf8("Value")])
        self.responseHeadersList.setModel(self.__replyHeaders)
        self.responseHeadersList.horizontalHeader().setStretchLastSection(True)
        self.connect(self.responseHeadersList, 
                     SIGNAL("doubleClicked(const QModelIndex&)"), 
                     self.__showHeaderDetails)
        
        self.requestsList.horizontalHeader().setStretchLastSection(True)
        self.requestsList.verticalHeader().setMinimumSectionSize(-1)
        
        self.__proxyModel = QSortFilterProxyModel(self)
        self.__proxyModel.setFilterKeyColumn(-1)
        self.connect(self.searchEdit, SIGNAL("textChanged(QString)"), 
                     self.__proxyModel.setFilterFixedString)
        
        self.connect(self.removeButton, SIGNAL("clicked()"), 
            self.requestsList.removeSelected)
        self.connect(self.removeAllButton, SIGNAL("clicked()"), 
            self.requestsList.removeAll)
        
        self.__model = E4RequestModel(networkAccessManager, self)
        self.__proxyModel.setSourceModel(self.__model)
        self.requestsList.setModel(self.__proxyModel)
        self.connect(self.requestsList.selectionModel(), 
                     SIGNAL("currentChanged(const QModelIndex&, const QModelIndex&)"), 
                     self.__currentChanged)
        
        fm = self.fontMetrics()
        em = fm.width("m")
        self.requestsList.horizontalHeader().resizeSection(0, em *  5)
        self.requestsList.horizontalHeader().resizeSection(1, em * 20)
        self.requestsList.horizontalHeader().resizeSection(3, em *  5)
        self.requestsList.horizontalHeader().resizeSection(4, em * 15)
        
        self.__headersDlg = None
    
    def closeEvent(self, evt):
        """
        Protected method called upon closing the dialog.
        
        @param evt reference to the close event object (QCloseEvent)
        """
        self.deleteLater()
        self.__class__._monitor = None
        QDialog.closeEvent(self, evt)
    
    def reject(self):
        """
        Public slot to close the dialog with a Reject status.
        """
        self.__class__._monitor = None
        QDialog.reject(self)
    
    def __currentChanged(self, current, previous):
        """
        Private slot to handle a change of the current index.
        
        @param current new current index (QModelIndex)
        @param previous old current index (QModelIndex)
        """
        self.__requestHeaders.setRowCount(0)
        self.__replyHeaders.setRowCount(0)
        
        if not current.isValid():
            return
        
        row = self.__proxyModel.mapToSource(current).row()
        
        req = self.__model.requests[row].request
        
        for header in req.rawHeaderList():
            self.__requestHeaders.insertRows(0, 1, QModelIndex())
            self.__requestHeaders.setData(
                self.__requestHeaders.index(0, 0), 
                QVariant(QString(header)))
            self.__requestHeaders.setData(
                self.__requestHeaders.index(0, 1), 
                QVariant(QString(req.rawHeader(header))))
            self.__requestHeaders.item(0, 0).setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.__requestHeaders.item(0, 1).setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        
        for header in self.__model.requests[row].replyHeaders:
            self.__replyHeaders.insertRows(0, 1, QModelIndex())
            self.__replyHeaders.setData(
                self.__replyHeaders.index(0, 0), 
                QVariant(QString(header[0])))
            self.__replyHeaders.setData(
                self.__replyHeaders.index(0, 1), 
                QVariant(QString(header[1])))
            self.__replyHeaders.item(0, 0).setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.__replyHeaders.item(0, 1).setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsEnabled)
    
    def __showHeaderDetails(self, index):
        """
        Private slot to show a dialog with the header details.
        
        @param index index of the entry to show (QModelIndex)
        """
        if not index.isValid():
            return
        
        headerList = self.sender()
        if headerList is None:
            return
        
        row = index.row()
        name = headerList.model().data(headerList.model().index(row, 0)).toString()
        value = headerList.model().data(headerList.model().index(row, 1)).toString()
        if self.__headersDlg is None:
            self.__headersDlg = E4NetworkHeaderDetailsDialog(self)
        self.__headersDlg.setData(name, value)
        self.__headersDlg.show()

class E4RequestModel(QAbstractTableModel):
    """
    Class implementing a model storing request objects.
    """
    def __init__(self, networkAccessManager, parent = None):
        """
        Constructor
        
        @param networkAccessManager reference to the network access manager
            (QNetworkAccessManager)
        @param parent reference to the parent object (QObject)
        """
        QAbstractTableModel.__init__(self, parent)
        
        self.__headerData = [
            self.trUtf8("Method"), 
            self.trUtf8("Address"), 
            self.trUtf8("Response"), 
            self.trUtf8("Length"), 
            self.trUtf8("Content Type"), 
            self.trUtf8("Info"), 
        ]
        
        self.__operations = {
            QNetworkAccessManager.HeadOperation : "HEAD", 
            QNetworkAccessManager.GetOperation  : "GET", 
            QNetworkAccessManager.PutOperation  : "PUT", 
            QNetworkAccessManager.PostOperation : "POST", 
        }
        
        self.requests = []
        self.connect(networkAccessManager, 
                     SIGNAL("requestCreated(QNetworkAccessManager::Operation, const QNetworkRequest&, QNetworkReply*)"), 
                     self.__requestCreated)
    
    def __requestCreated(self, operation, request, reply):
        """
        Private slot handling the creation of a network request.
        
        @param operation network operation (QNetworkAccessManager.Operation)
        @param request reference to the request object (QNetworkRequest)
        @param reply reference to the reply object(QNetworkReply)
        """
        req = E4NetworkRequest()
        req.op = operation
        req.request = QNetworkRequest(request)
        req.reply = reply
        self.__addRequest(req)
    
    def __addRequest(self, req):
        """
        Private method to add a request object to the model.
        
        @param req reference to the request object (E4NetworkRequest)
        """
        self.beginInsertRows(QModelIndex(), len(self.requests), len(self.requests))
        self.requests.append(req)
        self.connect(req.reply, SIGNAL("finished()"), self.__addReply)
        self.endInsertRows()
    
    def __addReply(self):
        """
        Private slot to add the reply data to the model.
        """
        reply = self.sender()
        if reply is None:
            return
        
        offset = len(self.requests) - 1
        while offset >= 0:
            if self.requests[offset].reply is reply:
                break
            offset -= 1
        if offset < 0:
            return
        
        # save the reply header data
        for header in reply.rawHeaderList():
            self.requests[offset].replyHeaders.append((header, reply.rawHeader(header)))
        
        # save reply info to be displayed
        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute).toInt()[0]
        reason = reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute).toString()
        self.requests[offset].response = "%d %s" % (status, reason)
        self.requests[offset].length = \
            reply.header(QNetworkRequest.ContentLengthHeader).toInt()[0]
        self.requests[offset].contentType = \
            reply.header(QNetworkRequest.ContentTypeHeader).toString()
        
        if status == 302:
            target = reply.attribute(QNetworkRequest.RedirectionTargetAttribute).toUrl()
            self.requests[offset].info = \
                self.trUtf8("Redirect: %1").arg(target.toString())
    
    def headerData(self, section, orientation, role):
        """
        Public method to get header data from the model.
        
        @param section section number (integer)
        @param orientation orientation (Qt.Orientation)
        @param role role of the data to retrieve (integer)
        @return requested data
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.__headerData[section])
        
        return QAbstractTableModel.headerData(self, section, orientation, role)
    
    def data(self, index, role):
        """
        Public method to get data from the model.
        
        @param index index to get data for (QModelIndex)
        @param role role of the data to retrieve (integer)
        @return requested data
        """
        if index.row() < 0 or index.row() >= len(self.requests):
            return QVariant()
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            col = index.column()
            if col == 0:
                try:
                    return QVariant(self.__operations[self.requests[index.row()].op])
                except KeyError:
                    return QVariant(self.trUtf8("Unknown"))
            elif col == 1:
                return QVariant(self.requests[index.row()].request.url().toEncoded())
            elif col == 2:
                return QVariant(self.requests[index.row()].response)
            elif col == 3:
                return QVariant(self.requests[index.row()].length)
            elif col == 4:
                return QVariant(self.requests[index.row()].contentType)
            elif col == 5:
                return QVariant(self.requests[index.row()].info)
        
        return QVariant()
    
    def columnCount(self, parent):
        """
        Public method to get the number of columns of the model.
        
        @param parent parent index (QModelIndex)
        @return number of columns (integer)
        """
        if parent.column() > 0:
            return 0
        else:
            return len(self.__headerData)
    
    def rowCount(self, parent):
        """
        Public method to get the number of rows of the model.
        
        @param parent parent index (QModelIndex)
        @return number of columns (integer)
        """
        if parent.isValid():
            return 0
        else:
            return len(self.requests)
    
    def removeRows(self, row, count, parent):
        """
        Public method to remove entries from the model.
        
        @param row start row (integer)
        @param count number of rows to remove (integer)
        @param parent parent index (QModelIndex)
        @return flag indicating success (boolean)
        """
        if parent.isValid():
            return False
        
        lastRow = row + count - 1
        self.beginRemoveRows(parent, row, lastRow)
        del self.requests[row:lastRow + 1]
        self.endRemoveRows()
        return True
