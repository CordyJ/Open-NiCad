# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the history menu.
"""

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox

from E4Gui.E4ModelMenu import E4ModelMenu

import Helpviewer.HelpWindow

from HistoryModel import HistoryModel
from HistoryDialog import HistoryDialog

import UI.PixmapCache

class HistoryMenuModel(QAbstractProxyModel):
    """
    Class implementing a model for the history menu.
    
    It maps the first bunch of items of the source model to the root.
    """
    MOVEDROWS = 15
    
    def __init__(self, sourceModel, parent = None):
        """
        Constructor
        
        @param sourceModel reference to the source model (QAbstractItemModel)
        @param parent reference to the parent object (QObject)
        """
        QAbstractProxyModel.__init__(self, parent)
        
        self.__treeModel = sourceModel
        
        self.setSourceModel(sourceModel)
    
    def bumpedRows(self):
        """
        Public method to determine the number of rows moved to the root.
        
        @return number of rows moved to the root (integer)
        """
        first = self.__treeModel.index(0, 0)
        if not first.isValid():
            return 0
        return min(self.__treeModel.rowCount(first), self.MOVEDROWS)
    
    def columnCount(self, parent = QModelIndex()):
        """
        Public method to get the number of columns.
        
        @param parent index of parent (QModelIndex)
        @return number of columns (integer)
        """
        return self.__treeModel.columnCount(self.mapToSource(parent))
    
    def rowCount(self, parent = QModelIndex()):
        """
        Public method to determine the number of rows.
        
        @param parent index of parent (QModelIndex)
        @return number of rows (integer)
        """
        if parent.column() > 0:
            return 0
        
        if not parent.isValid():
            folders = self.sourceModel().rowCount()
            bumpedItems = self.bumpedRows()
            if bumpedItems <= self.MOVEDROWS and \
               bumpedItems == self.sourceModel().rowCount(self.sourceModel().index(0, 0)):
                folders -= 1
            return bumpedItems + folders
        
        if parent.internalId() == sys.maxint:
            if parent.row() < self.bumpedRows():
                return 0
        
        idx = self.mapToSource(parent)
        defaultCount = self.sourceModel().rowCount(idx)
        if idx == self.sourceModel().index(0, 0):
            return defaultCount - self.bumpedRows()
        
        return defaultCount
    
    def mapFromSource(self, sourceIndex):
        """
        Public method to map an index to the proxy model index.
        
        @param sourceIndex reference to a source model index (QModelIndex)
        @return proxy model index (QModelIndex)
        """
        assert False
        sourceRow = self.__treeModel.mapToSource(sourceIndex).row()
        return self.createIndex(sourceIndex.row(), sourceIndex.column(), sourceRow)
    
    def mapToSource(self, proxyIndex):
        """
        Public method to map an index to the source model index.
        
        @param proxyIndex reference to a proxy model index (QModelIndex)
        @return source model index (QModelIndex)
        """
        if not proxyIndex.isValid():
            return QModelIndex()
        
        if proxyIndex.internalId() == sys.maxint:
            bumpedItems = self.bumpedRows()
            if proxyIndex.row() < bumpedItems:
                return self.__treeModel.index(proxyIndex.row(), proxyIndex.column(), 
                    self.__treeModel.index(0, 0))
            if bumpedItems <= self.MOVEDROWS and \
               bumpedItems == self.sourceModel().rowCount(self.__treeModel.index(0, 0)):
                bumpedItems -= 1
            return self.__treeModel.index(proxyIndex.row() - bumpedItems, 
                                          proxyIndex.column())
        
        historyIndex = self.__treeModel.sourceModel()\
            .index(proxyIndex.internalId(), proxyIndex.column())
        treeIndex = self.__treeModel.mapFromSource(historyIndex)
        return treeIndex
    
    def index(self, row, column, parent = QModelIndex()):
        """
        Public method to create an index.
        
        @param row row number for the index (integer)
        @param column column number for the index (integer)
        @param parent index of the parent item (QModelIndex)
        @return requested index (QModelIndex)
        """
        if row < 0 or \
           column < 0 or \
           column >= self.columnCount(parent) or \
           parent.column() > 0:
            return QModelIndex()
        
        if not parent.isValid():
            return self.createIndex(row, column, sys.maxint)
        
        treeIndexParent = self.mapToSource(parent)
        
        bumpedItems = 0
        if treeIndexParent == self.sourceModel().index(0, 0):
            bumpedItems = self.bumpedRows()
        treeIndex = self.__treeModel.index(row + bumpedItems, column, treeIndexParent)
        historyIndex = self.__treeModel.mapToSource(treeIndex)
        historyRow = historyIndex.row()
        if historyRow == -1:
            historyRow = treeIndex.row()
        return self.createIndex(row, column, historyRow)

    def parent(self, index):
        """
        Public method to get the parent index.
        
        @param index index of item to get parent (QModelIndex)
        @return index of parent (QModelIndex)
        """
        offset = index.internalId()
        if offset == sys.maxint or not index.isValid():
            return QModelIndex()
        
        historyIndex = self.__treeModel.sourceModel().index(index.internalId(), 0)
        treeIndex = self.__treeModel.mapFromSource(historyIndex)
        treeIndexParent = treeIndex.parent()
        
        soureRow = self.sourceModel().mapToSource(treeIndexParent).row()
        bumpedItems = self.bumpedRows()
        if bumpedItems <= self.MOVEDROWS and \
           bumpedItems == self.sourceModel().rowCount(self.sourceModel().index(0, 0)):
            bumpedItems -= 1
        
        return self.createIndex(bumpedItems + treeIndexParent.row(), 
                                treeIndexParent.column(), 
                                sourceRow)
    
    def mimeData(self, indexes):
        """
        Public method to return the mime data.
        
        @param indexes list of indexes (QModelIndexList)
        @return mime data (QMimeData)
        """
        urls = []
        for index in indexes:
            url = index.data(HistoryModel.UrlRole).toUrl()
            urls.append(url)
        
        mdata = QMimeData()
        mdata.setUrls(urls)
        return mdata

class HistoryMenu(E4ModelMenu):
    """
    Class implementing the history menu.
    
    @signal openUrl(const QUrl&, const QString&) emitted to open a URL in the current
            tab
    @signal newUrl(const QUrl&, const QString&) emitted to open a URL in a new tab
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        E4ModelMenu.__init__(self, parent)
        
        self.__historyManager = None
        self.__historyMenuModel = None
        self.__initialActions = []
        
        self.setMaxRows(7)
        
        self.connect(self, SIGNAL("activated(const QModelIndex&)"), self.__activated)
        self.setStatusBarTextRole(HistoryModel.UrlStringRole)
    
    def __activated(self, idx):
        """
        Private slot handling the activated signal.
        
        @param idx index of the activated item (QModelIndex)
        """
        if self._keyboardModifiers & Qt.ControlModifier:
            self.emit(SIGNAL("newUrl(const QUrl&, const QString&)"), 
                      idx.data(HistoryModel.UrlRole).toUrl(), 
                      idx.data(HistoryModel.TitleRole).toString())
        else:
            self.emit(SIGNAL("openUrl(const QUrl&, const QString&)"), 
                      idx.data(HistoryModel.UrlRole).toUrl(), 
                      idx.data(HistoryModel.TitleRole).toString())
    
    def prePopulated(self):
        """
        Public method to add any actions before the tree.
       
        @return flag indicating if any actions were added
        """
        if self.__historyManager is None:
            self.__historyManager = Helpviewer.HelpWindow.HelpWindow.historyManager()
            self.__historyMenuModel = \
                HistoryMenuModel(self.__historyManager.historyTreeModel(), self)
            self.setModel(self.__historyMenuModel)
        
        # initial actions
        for act in self.__initialActions:
            self.addAction(act)
        if len(self.__initialActions) != 0:
            self.addSeparator()
        self.setFirstSeparator(self.__historyMenuModel.bumpedRows())
        
        return False
    
    def postPopulated(self):
        """
        Public method to add any actions after the tree.
        """
        if len(self.__historyManager.history()) > 0:
            self.addSeparator()
        
        act = self.addAction(UI.PixmapCache.getIcon("history.png"), 
                             self.trUtf8("Show All History..."))
        self.connect(act, SIGNAL("triggered()"), self.__showHistoryDialog)
        act = self.addAction(UI.PixmapCache.getIcon("historyClear.png"), 
                             self.trUtf8("Clear History..."))
        self.connect(act, SIGNAL("triggered()"), self.__clearHistoryDialog)
    
    def setInitialActions(self, actions):
        """
        Public method to set the list of actions that should appear first in the menu.
        
        @param actions list of initial actions (list of QAction)
        """
        self.__initialActions = actions[:]
        for act in self.__initialActions:
            self.addAction(act)
    
    def __showHistoryDialog(self):
        """
        Private slot to show the history dialog.
        """
        dlg = HistoryDialog(self)
        dlg.setAttribute(Qt.WA_DeleteOnClose)
        self.connect(dlg,  SIGNAL("newUrl(const QUrl&, const QString&)"), 
                     self, SIGNAL("newUrl(const QUrl&, const QString&)"))
        self.connect(dlg,  SIGNAL("openUrl(const QUrl&, const QString&)"), 
                     self, SIGNAL("openUrl(const QUrl&, const QString&)"))
        dlg.show()
    
    def __clearHistoryDialog(self):
        """
        Private slot to clear the history.
        """
        if self.__historyManager is not None and \
           KQMessageBox.question(None,
                self.trUtf8("Clear History"),
                self.trUtf8("""Do you want to clear the history?"""),
                QMessageBox.StandardButtons(\
                    QMessageBox.No | \
                    QMessageBox.Yes),
                QMessageBox.No) == QMessageBox.Yes:
            self.__historyManager.clear()
