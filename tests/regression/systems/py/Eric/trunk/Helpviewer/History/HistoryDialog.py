# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to manage history.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from E4Gui.E4TreeSortFilterProxyModel import E4TreeSortFilterProxyModel

import Helpviewer.HelpWindow
from HistoryModel import HistoryModel

from Ui_HistoryDialog import Ui_HistoryDialog

import UI.PixmapCache

class HistoryDialog(QDialog, Ui_HistoryDialog):
    """
    Class implementing a dialog to manage history.
    
    @signal openUrl(const QUrl&, const QString&) emitted to open a URL in the current
            tab
    @signal newUrl(const QUrl&, const QString&) emitted to open a URL in a new tab
    """
    def __init__(self, parent = None, manager = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget
        @param manager reference to the history manager object (HistoryManager)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.clearButton.setIcon(UI.PixmapCache.getIcon("clearLeft.png"))
        
        self.__historyManager = manager
        if self.__historyManager is None:
            self.__historyManager = Helpviewer.HelpWindow.HelpWindow.historyManager()
        
        self.__model = self.__historyManager.historyTreeModel()
        self.__proxyModel = E4TreeSortFilterProxyModel(self)
        self.__proxyModel.setSortRole(HistoryModel.DateTimeRole)
        self.__proxyModel.setFilterKeyColumn(-1)
        self.__proxyModel.setSourceModel(self.__model)
        self.historyTree.setModel(self.__proxyModel)
        self.historyTree.expandAll()
        fm = QFontMetrics(self.font())
        header = fm.width("m") * 40
        self.historyTree.header().resizeSection(0, header)
        self.historyTree.header().setStretchLastSection(True)
        self.historyTree.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.connect(self.historyTree, SIGNAL("activated(const QModelIndex&)"), 
                     self.__activated)
        self.connect(self.historyTree, 
                     SIGNAL("customContextMenuRequested(const QPoint &)"), 
                     self.__customContextMenuRequested)
        
        self.connect(self.searchEdit, SIGNAL("textChanged(QString)"), 
                     self.__proxyModel.setFilterFixedString)
        self.connect(self.removeButton, SIGNAL("clicked()"), 
                     self.historyTree.removeSelected)
        self.connect(self.removeAllButton, SIGNAL("clicked()"), 
                     self.__historyManager.clear)
        
        self.connect(self.__proxyModel, SIGNAL("modelReset()"), self.__modelReset)
    
    def __modelReset(self):
        """
        Private slot handling a reset of the tree view's model.
        """
        self.historyTree.expandAll()
    
    def __customContextMenuRequested(self, pos):
        """
        Private slot to handle the context menu request for the bookmarks tree.
        
        @param pos position the context menu was requested (QPoint)
        """
        menu = QMenu()
        idx = self.historyTree.indexAt(pos)
        idx = idx.sibling(idx.row(), 0)
        if idx.isValid() and not self.historyTree.model().hasChildren(idx):
            menu.addAction(self.trUtf8("&Open"), self.__openHistoryInCurrentTab)
            menu.addAction(self.trUtf8("Open in New &Tab"), self.__openHistoryInNewTab)
            menu.addSeparator()
            menu.addAction(self.trUtf8("&Copy"), self.__copyHistory)
        menu.addAction(self.trUtf8("&Remove"), self.historyTree.removeSelected)
        menu.exec_(QCursor.pos())
    
    def __activated(self, idx):
        """
        Private slot to handle the activation of an entry.
        
        @param idx reference to the entry index (QModelIndex)
        """
        self.__openHistory(QApplication.keyboardModifiers() & Qt.ControlModifier)
        
    def __openHistoryInCurrentTab(self):
        """
        Private slot to open a history entry in the current browser tab.
        """
        self.__openHistory(False)
    
    def __openHistoryInNewTab(self):
        """
        Private slot to open a history entry in a new browser tab.
        """
        self.__openHistory(True)
    
    def __openHistory(self, newTab):
        """
        Private method to open a history entry.
        
        @param newTab flag indicating to open the history entry in a new tab (boolean)
        """
        idx = self.historyTree.currentIndex()
        if newTab:
            self.emit(SIGNAL("newUrl(const QUrl&, const QString&)"), 
                      idx.data(HistoryModel.UrlRole).toUrl(), 
                      idx.data(HistoryModel.TitleRole).toString())
        else:
            self.emit(SIGNAL("openUrl(const QUrl&, const QString&)"), 
                      idx.data(HistoryModel.UrlRole).toUrl(), 
                      idx.data(HistoryModel.TitleRole).toString())
    
    def __copyHistory(self):
        """
        Private slot to copy a history entry's URL to the clipboard.
        """
        idx = self.historyTree.currentIndex()
        if not idx.parent().isValid():
            return
        
        url = idx.data(HistoryModel.UrlStringRole).toString()
        
        clipboard = QApplication.clipboard()
        clipboard.setText(url)
