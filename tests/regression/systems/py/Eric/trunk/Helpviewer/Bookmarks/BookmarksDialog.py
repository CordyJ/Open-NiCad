# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to manage bookmarks.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from E4Gui.E4TreeSortFilterProxyModel import E4TreeSortFilterProxyModel

import Helpviewer.HelpWindow
from BookmarkNode import BookmarkNode
from BookmarksModel import BookmarksModel

from Ui_BookmarksDialog import Ui_BookmarksDialog

import UI.PixmapCache

class BookmarksDialog(QDialog, Ui_BookmarksDialog):
    """
    Class implementing a dialog to manage bookmarks.
    
    @signal openUrl(const QUrl&, const QString&) emitted to open a URL in the current
            tab
    @signal newUrl(const QUrl&, const QString&) emitted to open a URL in a new tab
    """
    def __init__(self, parent = None, manager = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget
        @param manager reference to the bookmarks manager object (BookmarksManager)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.clearButton.setIcon(UI.PixmapCache.getIcon("clearLeft.png"))
        
        self.__bookmarksManager = manager
        if self.__bookmarksManager is None:
            self.__bookmarksManager = Helpviewer.HelpWindow.HelpWindow.bookmarksManager()
        
        self.__bookmarksModel = self.__bookmarksManager.bookmarksModel()
        self.__proxyModel = E4TreeSortFilterProxyModel(self)
        self.__proxyModel.setFilterKeyColumn(-1)
        self.__proxyModel.setSourceModel(self.__bookmarksModel)
        
        self.connect(self.searchEdit, SIGNAL("textChanged(QString)"), 
                     self.__proxyModel.setFilterFixedString)
        
        self.bookmarksTree.setModel(self.__proxyModel)
        self.bookmarksTree.setExpanded(self.__proxyModel.index(0, 0), True)
        fm = QFontMetrics(self.font())
        header = fm.width("m") * 40
        self.bookmarksTree.header().resizeSection(0, header)
        self.bookmarksTree.header().setStretchLastSection(True)
        self.bookmarksTree.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.connect(self.bookmarksTree, SIGNAL("activated(const QModelIndex&)"), 
                     self.__activated)
        self.connect(self.bookmarksTree, 
                     SIGNAL("customContextMenuRequested(const QPoint &)"), 
                     self.__customContextMenuRequested)
        
        self.connect(self.removeButton, SIGNAL("clicked()"), 
                     self.bookmarksTree.removeSelected)
        self.connect(self.addFolderButton, SIGNAL("clicked()"), 
                     self.__newFolder)
        
        self.__expandNodes(self.__bookmarksManager.bookmarks())
    
    def closeEvent(self, evt):
        """
        Protected method to handle the closing of the dialog.
        
        @param evt reference to the event object (QCloseEvent) (ignored)
        """
        self.__shutdown()
    
    def reject(self):
        """
        Protected method called when the dialog is rejected.
        """
        self.__shutdown()
        QDialog.reject(self)
    
    def __shutdown(self):
        """
        Private method to perform shutdown actions for the dialog.
        """
        if self.__saveExpandedNodes(self.bookmarksTree.rootIndex()):
            self.__bookmarksManager.changeExpanded()
    
    def __saveExpandedNodes(self, parent):
        """
        Private method to save the child nodes of an expanded node.
        
        @param parent index of the parent node (QModelIndex)
        @return flag indicating a change (boolean)
        """
        changed = False
        for row in range(self.__proxyModel.rowCount(parent)):
            child = self.__proxyModel.index(row, 0, parent)
            sourceIndex = self.__proxyModel.mapToSource(child)
            childNode = self.__bookmarksModel.node(sourceIndex)
            wasExpanded = childNode.expanded
            if self.bookmarksTree.isExpanded(child):
                childNode.expanded = True
                changed |= self.__saveExpandedNodes(child)
            else:
                childNode.expanded = False
            changed |= (wasExpanded != childNode.expanded)
        
        return changed
    
    def __expandNodes(self, node):
        """
        Private method to expand all child nodes of a node.
        
        @param node reference to the bookmark node to expand (BookmarkNode)
        """
        for childNode in node.children():
            if childNode.expanded:
                idx = self.__bookmarksModel.nodeIndex(childNode)
                idx = self.__proxyModel.mapFromSource(idx)
                self.bookmarksTree.setExpanded(idx, True)
                self.__expandNodes(childNode)
    
    def __customContextMenuRequested(self, pos):
        """
        Private slot to handle the context menu request for the bookmarks tree.
        
        @param pos position the context menu was requested (QPoint)
        """
        menu = QMenu()
        idx = self.bookmarksTree.indexAt(pos)
        idx = idx.sibling(idx.row(), 0)
        sourceIndex = self.__proxyModel.mapToSource(idx)
        node = self.__bookmarksModel.node(sourceIndex)
        if idx.isValid() and node.type() != BookmarkNode.Folder:
            menu.addAction(self.trUtf8("&Open"), self.__openBookmarkInCurrentTab)
            menu.addAction(self.trUtf8("Open in New &Tab"), self.__openBookmarkInNewTab)
            menu.addSeparator()
        act = menu.addAction(self.trUtf8("Edit &Name"), self.__editName)
        act.setEnabled(idx.flags() & Qt.ItemIsEditable)
        if idx.isValid() and node.type() != BookmarkNode.Folder:
            menu.addAction(self.trUtf8("Edit &Address"), self.__editAddress)
        menu.addSeparator()
        act = menu.addAction(self.trUtf8("&Delete"), self.bookmarksTree.removeSelected)
        act.setEnabled(idx.flags() & Qt.ItemIsDragEnabled)
        menu.exec_(QCursor.pos())
    
    def __activated(self, idx):
        """
        Private slot to handle the activation of an entry.
        
        @param idx reference to the entry index (QModelIndex)
        """
        self.__openBookmark(QApplication.keyboardModifiers() & Qt.ControlModifier)
        
    def __openBookmarkInCurrentTab(self):
        """
        Private slot to open a bookmark in the current browser tab.
        """
        self.__openBookmark(False)
    
    def __openBookmarkInNewTab(self):
        """
        Private slot to open a bookmark in a new browser tab.
        """
        self.__openBookmark(True)
    
    def __openBookmark(self, newTab):
        """
        Private method to open a bookmark.
        
        @param newTab flag indicating to open the bookmark in a new tab (boolean)
        """
        idx = self.bookmarksTree.currentIndex()
        sourceIndex = self.__proxyModel.mapToSource(idx)
        node = self.__bookmarksModel.node(sourceIndex)
        if not idx.parent().isValid() or \
           node is None or \
           node.type() == BookmarkNode.Folder:
            return
        if newTab:
            self.emit(SIGNAL("newUrl(const QUrl&, const QString&)"), 
                      idx.sibling(idx.row(), 1).data(BookmarksModel.UrlRole).toUrl(), 
                      idx.sibling(idx.row(), 0).data(Qt.DisplayRole).toString())
        else:
            self.emit(SIGNAL("openUrl(const QUrl&, const QString&)"), 
                      idx.sibling(idx.row(), 1).data(BookmarksModel.UrlRole).toUrl(), 
                      idx.sibling(idx.row(), 0).data(Qt.DisplayRole).toString())
    
    def __editName(self):
        """
        Private slot to edit the name part of a bookmark.
        """
        idx = self.bookmarksTree.currentIndex()
        idx = idx.sibling(idx.row(), 0)
        self.bookmarksTree.edit(idx)
    
    def __editAddress(self):
        """
        Private slot to edit the address part of a bookmark.
        """
        idx = self.bookmarksTree.currentIndex()
        idx = idx.sibling(idx.row(), 1)
        self.bookmarksTree.edit(idx)
    
    def __newFolder(self):
        """
        Private slot to add a new bookmarks folder.
        """
        currentIndex = self.bookmarksTree.currentIndex()
        idx = QModelIndex(currentIndex)
        sourceIndex = self.__proxyModel.mapToSource(idx)
        sourceNode = self.__bookmarksModel.node(sourceIndex)
        row = -1    # append new folder as the last item per default
        
        if sourceNode is not None and \
           sourceNode.type() != BookmarkNode.Folder:
            # If the selected item is not a folder, add a new folder to the
            # parent folder, but directly below the selected item.
            idx = idx.parent()
            row = currentIndex.row() + 1
        
        if not idx.isValid():
            # Select bookmarks menu as default.
            idx = self.__proxyModel.index(1, 0)
        
        idx = self.__proxyModel.mapToSource(idx)
        parent = self.__bookmarksModel.node(idx)
        node = BookmarkNode(BookmarkNode.Folder)
        node.title = self.trUtf8("New Folder")
        self.__bookmarksManager.addBookmark(parent, node, row)
