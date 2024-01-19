# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a tool bar showing bookmarks.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from E4Gui.E4ModelToolBar import E4ModelToolBar

import Helpviewer.HelpWindow

from BookmarksModel import BookmarksModel
from BookmarkNode import BookmarkNode
from BookmarksMenu import BookmarksMenu
from AddBookmarkDialog import AddBookmarkDialog

import UI.PixmapCache

class BookmarksToolBar(E4ModelToolBar):
    """
    Class implementing a tool bar showing bookmarks.
    
    @signal openUrl(const QUrl&, const QString&) emitted to open a URL in the current
            tab
    @signal newUrl(const QUrl&, const QString&) emitted to open a URL in a new tab
    """
    def __init__(self, model, parent = None):
        """
        Constructor
        
        @param model reference to the bookmarks model (BookmarksModel)
        @param parent reference to the parent widget (QWidget)
        """
        E4ModelToolBar.__init__(self, 
            QApplication.translate("BookmarksToolBar", "Bookmarks"), parent)
        
        self.__bookmarksModel = model
        
        self.setModel(model)
        self.setRootIndex(model.nodeIndex(
            Helpviewer.HelpWindow.HelpWindow.bookmarksManager().toolbar()))
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL("customContextMenuRequested(const QPoint &)"), 
                     self.__contextMenuRequested)
        self.connect(self, SIGNAL("activated(const QModelIndex &)"), 
                     self.__bookmarkActivated)
        
        self.setHidden(True)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        self._build()
    
    def __contextMenuRequested(self, pos):
        """
        Private slot to handle the context menu request.
        
        @param pos position the context menu shall be shown (QPoint)
        """
        act = self.actionAt(pos)
        menu = QMenu()
        
        if act is not None:
            v = act.data()
            
            if act.menu() is None:
                menuAction = menu.addAction(self.trUtf8("&Open"), self.__openBookmark)
                menuAction.setData(v)
                
                menuAction = menu.addAction(self.trUtf8("Open in New &Tab\tCtrl+LMB"), 
                    self.__openBookmarkInNewTab)
                menuAction.setData(v)
                
                menu.addSeparator()
            
            menuAction = menu.addAction(self.trUtf8("&Remove"), self.__removeBookmark)
            menuAction.setData(v)
            
            menu.addSeparator()
        
        menu.addAction(self.trUtf8("Add &Bookmark..."), self.__newBookmark)
        menu.addAction(self.trUtf8("Add &Folder..."), self.__newFolder)
        
        menu.exec_(QCursor.pos())
    
    def __bookmarkActivated(self, idx):
        """
        Private slot handling the activation of a bookmark.
        
        @param idx index of the activated bookmark (QModelIndex)
        """
        assert idx.isValid()
        
        if self._keyboardModifiers & Qt.ControlModifier:
            self.emit(SIGNAL("newUrl(const QUrl&, const QString&)"), 
                      idx.data(BookmarksModel.UrlRole).toUrl(), 
                      idx.data(Qt.DisplayRole).toString())
        else:
            self.emit(SIGNAL("openUrl(const QUrl&, const QString&)"), 
                      idx.data(BookmarksModel.UrlRole).toUrl(), 
                      idx.data(Qt.DisplayRole).toString())
    
    def __openToolBarBookmark(self):
        """
        Private slot to open a bookmark in the current browser tab.
        """
        idx = self.index(self.sender())
        
        if self._keyboardModifiers & Qt.ControlModifier:
            self.emit(SIGNAL("newUrl(const QUrl&, const QString&)"), 
                      idx.data(BookmarksModel.UrlRole).toUrl(), 
                      idx.data(Qt.DisplayRole).toString())
        else:
            self.emit(SIGNAL("openUrl(const QUrl&, const QString&)"), 
                      idx.data(BookmarksModel.UrlRole).toUrl(), 
                      idx.data(Qt.DisplayRole).toString())
        self.resetFlags()
    
    def __openBookmark(self):
        """
        Private slot to open a bookmark in the current browser tab.
        """
        idx = self.index(self.sender())
        
        self.emit(SIGNAL("openUrl(const QUrl&, const QString&)"), 
                  idx.data(BookmarksModel.UrlRole).toUrl(), 
                  idx.data(Qt.DisplayRole).toString())
    
    def __openBookmarkInNewTab(self):
        """
        Private slot to open a bookmark in a new browser tab.
        """
        idx = self.index(self.sender())
        
        self.emit(SIGNAL("newUrl(const QUrl&, const QString&)"), 
                  idx.data(BookmarksModel.UrlRole).toUrl(), 
                  idx.data(Qt.DisplayRole).toString())
    
    def __removeBookmark(self):
        """
        Private slot to remove a bookmark.
        """
        idx = self.index(self.sender())
        
        self.__bookmarksModel.removeRow(idx.row(), self.rootIndex())
    
    def __newBookmark(self):
        """
        Private slot to add a new bookmark.
        """
        dlg = AddBookmarkDialog()
        dlg.setCurrentIndex(self.rootIndex())
        dlg.exec_()
    
    def __newFolder(self):
        """
        Private slot to add a new bookmarks folder.
        """
        dlg = AddBookmarkDialog()
        dlg.setCurrentIndex(self.rootIndex())
        dlg.setFolder(True)
        dlg.exec_()
    
    def _createMenu(self):
        """
        Protected method to create the menu for a tool bar action.
        
        @return menu for a tool bar action (E4ModelMenu)
        """
        menu = BookmarksMenu(self)
        self.connect(menu, SIGNAL("openUrl(const QUrl&, const QString&)"), 
                     self, SIGNAL("openUrl(const QUrl&, const QString&)"))
        self.connect(menu, SIGNAL("newUrl(const QUrl&, const QString&)"), 
                     self, SIGNAL("newUrl(const QUrl&, const QString&)"))
        return menu
