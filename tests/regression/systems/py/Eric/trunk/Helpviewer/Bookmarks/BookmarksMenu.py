# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the bookmarks menu.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from E4Gui.E4ModelMenu import E4ModelMenu

import Helpviewer.HelpWindow

from BookmarksModel import BookmarksModel
from BookmarkNode import BookmarkNode

class BookmarksMenu(E4ModelMenu):
    """
    Class implementing the bookmarks menu base class.
    
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
        
        self.connect(self, SIGNAL("activated(const QModelIndex&)"), self.__activated)
        self.setStatusBarTextRole(BookmarksModel.UrlStringRole)
        self.setSeparatorRole(BookmarksModel.SeparatorRole)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL("customContextMenuRequested(const QPoint &)"), 
                     self.__contextMenuRequested)
    
    def createBaseMenu(self):
        """
        Public method to get the menu that is used to populate sub menu's.
        
        @return reference to the menu (BookmarksMenu)
        """
        menu = BookmarksMenu(self)
        self.connect(menu, SIGNAL("openUrl(const QUrl&, const QString&)"), 
                     self, SIGNAL("openUrl(const QUrl&, const QString&)"))
        self.connect(menu, SIGNAL("newUrl(const QUrl&, const QString&)"), 
                     self, SIGNAL("newUrl(const QUrl&, const QString&)"))
        return menu
    
    def __activated(self, idx):
        """
        Private slot handling the activated signal.
        
        @param idx index of the activated item (QModelIndex)
        """
        if self._keyboardModifiers & Qt.ControlModifier:
            self.emit(SIGNAL("newUrl(const QUrl&, const QString&)"), 
                      idx.data(BookmarksModel.UrlRole).toUrl(), 
                      idx.data(Qt.DisplayRole).toString())
        else:
            self.emit(SIGNAL("openUrl(const QUrl&, const QString&)"), 
                      idx.data(BookmarksModel.UrlRole).toUrl(), 
                      idx.data(Qt.DisplayRole).toString())
        self.resetFlags()
    
    def postPopulated(self):
        """
        Public method to add any actions after the tree.
        """
        if self.isEmpty():
            return
        
        parent = self.rootIndex()
        
        hasBookmarks = False
        
        for i in range(parent.model().rowCount(parent)):
            child = parent.model().index(i, 0, parent)
            
            if child.data(BookmarksModel.TypeRole).toInt()[0] == BookmarkNode.Bookmark:
                hasBookmarks = True
                break
        
        if not hasBookmarks:
            return
        
        self.addSeparator()
        act = self.addAction(self.trUtf8("Open all in Tabs"))
        self.connect(act, SIGNAL("triggered()"), self.__openAll)
    
    def __openAll(self):
        """
        Private slot to open all the menu's items.
        """
        menu = self.sender().parent()
        if menu is None:
            return
        
        parent = menu.rootIndex()
        if not parent.isValid():
            return
        
        for i in range(parent.model().rowCount(parent)):
            child = parent.model().index(i, 0, parent)
            
            if child.data(BookmarksModel.TypeRole).toInt()[0] != BookmarkNode.Bookmark:
                continue
            
            if i == 0:
                self.emit(SIGNAL("openUrl(const QUrl&, const QString&)"),
                          child.data(BookmarksModel.UrlRole).toUrl(), 
                          child.data(Qt.DisplayRole).toString())
            else:
                self.emit(SIGNAL("newUrl(const QUrl&, const QString&)"),
                          child.data(BookmarksModel.UrlRole).toUrl(), 
                          child.data(Qt.DisplayRole).toString())
    
    def __contextMenuRequested(self, pos):
        """
        Private slot to handle the context menu request.
        
        @param pos position the context menu shall be shown (QPoint)
        """
        act = self.actionAt(pos)
        
        if act is not None and act.menu() is None and self.index(act).isValid():
            menu = QMenu()
            v = act.data()
            
            menuAction = menu.addAction(self.trUtf8("&Open"), self.__openBookmark)
            menuAction.setData(v)
            
            menuAction = menu.addAction(self.trUtf8("Open in New &Tab\tCtrl+LMB"), 
                self.__openBookmarkInNewTab)
            menuAction.setData(v)
        
            menu.addSeparator()
            
            menuAction = menu.addAction(self.trUtf8("&Remove"), self.__removeBookmark)
            menuAction.setData(v)
            
            execAct = menu.exec_(QCursor.pos())
            if execAct is not None:
                self.close()
                parent = self.parent()
                while parent is not None and isinstance(parent, QMenu):
                    parent.close()
                    parent = parent.parent()
    
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
        self.removeEntry(idx)

##########################################################################################

class BookmarksMenuBarMenu(BookmarksMenu):
    """
    Class implementing a dynamically populated menu for bookmarks.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        BookmarksMenu.__init__(self, parent)
        
        self.__bookmarksManager = None
        self.__initialActions = []
    
    def prePopulated(self):
        """
        Public method to add any actions before the tree.
       
        @return flag indicating if any actions were added
        """
        self.__bookmarksManager = Helpviewer.HelpWindow.HelpWindow.bookmarksManager()
        self.setModel(self.__bookmarksManager.bookmarksModel())
        self.setRootIndex(self.__bookmarksManager.bookmarksModel()\
                            .nodeIndex(self.__bookmarksManager.menu()))
        
        # initial actions
        for act in self.__initialActions:
            self.addAction(act)
        if len(self.__initialActions) != 0:
            self.addSeparator()
        
        self.createMenu(
            self.__bookmarksManager.bookmarksModel()\
                .nodeIndex(self.__bookmarksManager.toolbar()),
            1, self)
        return True
    
    def setInitialActions(self, actions):
        """
        Public method to set the list of actions that should appear first in the menu.
        
        @param actions list of initial actions (list of QAction)
        """
        self.__initialActions = actions[:]
        for act in self.__initialActions:
            self.addAction(act)
