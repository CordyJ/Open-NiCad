# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a menu populated from a QAbstractItemModel.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import UI.PixmapCache

class E4ModelMenu(QMenu):
    """
    Class implementing a menu populated from a QAbstractItemModel.
    
    @signal activated(const QModelIndex&) emitted when an action has been triggered
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        QMenu.__init__(self, parent)
        
        self.__maxRows = -1
        self.__firstSeparator = -1
        self.__maxWidth = -1
        self.__statusBarTextRole = 0
        self.__separatorRole = 0
        self.__model = None
        self.__root = QModelIndex()
        self.__dragStartPosition = QPoint()
        
        self.setAcceptDrops(True)
        
        self._mouseButton = Qt.NoButton
        self._keyboardModifiers = Qt.KeyboardModifiers(Qt.NoModifier)
        self.__dropRow = -1
        self.__dropIndex = None
        
        self.connect(self, SIGNAL("aboutToShow()"), self.__aboutToShow)
        self.connect(self, SIGNAL("triggered(QAction*)"), self.__actionTriggered)
    
    def prePopulated(self):
        """
        Public method to add any actions before the tree.
       
        @return flag indicating if any actions were added
        """
        return False
    
    def postPopulated(self):
        """
        Public method to add any actions after the tree.
        """
        pass
    
    def setModel(self, model):
        """
        Public method to set the model for the menu.
        
        @param model reference to the model (QAbstractItemModel)
        """
        self.__model = model
    
    def model(self):
        """
        Public method to get a reference to the model.
        
        @return reference to the model (QAbstractItemModel)
        """
        return self.__model
    
    def setMaxRows(self, rows):
        """
        Public method to set the maximum number of entries to show.
        
        @param rows maximum number of entries to show (integer)
        """
        self.__maxRows = rows
    
    def maxRows(self):
        """
        Public method to get the maximum number of entries to show.
        
        @return maximum number of entries to show (integer)
        """
        return self.__maxRows
    
    def setFirstSeparator(self, offset):
        """
        Public method to set the first separator.
        
        @param offset row number of the first separator (integer)
        """
        self.__firstSeparator = offset
    
    def firstSeparator(self):
        """
        Public method to get the first separator.
        
        @return row number of the first separator (integer)
        """
        return self.__firstSeparator
    
    def setRootIndex(self, index):
        """
        Public method to set the index of the root item.
        
        @param index index of the root item (QModelIndex)
        """
        self.__root = index
    
    def rootIndex(self):
        """
        Public method to get the index of the root item.
        
        @return index of the root item (QModelIndex)
        """
        return self.__root
    
    def setStatusBarTextRole(self, role):
        """
        Public method to set the role of the status bar text.
        
        @param role role of the status bar text (integer)
        """
        self.__statusBarTextRole = role
    
    def statusBarTextRole(self):
        """
        Public method to get the role of the status bar text.
        
        @return role of the status bar text (integer)
        """
        return self.__statusBarTextRole
    
    def setSeparatorRole(self, role):
        """
        Public method to set the role of the separator.
        
        @param role role of the separator (integer)
        """
        self.__separatorRole = role
    
    def separatorRole(self):
        """
        Public method to get the role of the separator.
        
        @return role of the separator (integer)
        """
        return self.__separatorRole
    
    def __aboutToShow(self):
        """
        Private slot to show the menu.
        """
        self.clear()
        
        if self.prePopulated():
            self.addSeparator()
        max_ = self.__maxRows
        if max_ != -1:
            max_ += self.__firstSeparator
        self.createMenu(self.__root, max_, self, self)
        self.postPopulated()
    
    def createBaseMenu(self):
        """
        Public method to get the menu that is used to populate sub menu's.
        
        @return reference to the menu (E4ModelMenu)
        """
        return E4ModelMenu(self)
    
    def createMenu(self, parent, max_, parentMenu = None, menu = None):
        """
        Public method to put all the children of a parent into a menu of a given length.
        
        @param parent index of the parent item (QModelIndex)
        @param max_ maximum number of entries (integer)
        @param parentMenu reference to the parent menu (QMenu)
        @param menu reference to the menu to be populated (QMenu)
        """
        if menu is None:
            v = QVariant(parent)
            
            title = parent.data().toString()
            modelMenu = self.createBaseMenu()
            # triggered goes all the way up the menu structure
            self.disconnect(modelMenu, SIGNAL("triggered(QAction*)"), 
                            modelMenu.__actionTriggered)
            modelMenu.setTitle(title)
            
            icon = parent.data(Qt.DecorationRole).toPyObject()
            if icon == NotImplemented or icon is None:
                icon = UI.PixmapCache.getIcon("defaultIcon.png")
            modelMenu.setIcon(icon)
            if parentMenu is not None:
                parentMenu.addMenu(modelMenu).setData(v)
            modelMenu.setRootIndex(parent)
            modelMenu.setModel(self.__model)
            return
        
        if self.__model is None:
            return
        
        end = self.__model.rowCount(parent)
        if max_ != -1:
            end = min(max_, end)
        
        for i in range(end):
            idx = self.__model.index(i, 0, parent)
            if self.__model.hasChildren(idx):
                self.createMenu(idx, -1, menu)
            else:
                if self.__separatorRole != 0 and idx.data(self.__separatorRole).toBool():
                    self.addSeparator()
                else:
                    menu.addAction(self.__makeAction(idx))
            
            if menu == self and i == self.__firstSeparator - 1:
                self.addSeparator()
    
    def __makeAction(self, idx):
        """
        Private method to create an action.
        
        @param idx index of the item to create an action for (QModelIndex)
        @return reference to the created action (QAction)
        """
        icon = idx.data(Qt.DecorationRole).toPyObject()
        if icon == NotImplemented or icon is None:
            icon = UI.PixmapCache.getIcon("defaultIcon.png")
        action = self.makeAction(icon, idx.data().toString(), self)
        action.setStatusTip(idx.data(self.__statusBarTextRole).toString())
        
        v = QVariant(idx)
        action.setData(v)
        
        return action
    
    def makeAction(self, icon, text, parent):
        """
        Public method to create an action.
        
        @param icon icon of the action (QIcon)
        @param text text of the action (QString)
        @param reference to the parent object (QObject)
        @return reference to the created action (QAction)
        """
        fm = QFontMetrics(self.font())
        if self.__maxWidth == -1:
            self.__maxWidth = fm.width('m') * 30
        smallText = fm.elidedText(text, Qt.ElideMiddle, self.__maxWidth)
        
        return QAction(icon, smallText, parent)
    
    def __actionTriggered(self, action):
        """
        Private slot to handle the triggering of an action.
        
        @param action reference to the action that was triggered (QAction)
        """
        idx = self.index(action)
        if idx.isValid():
            self.emit(SIGNAL("activated(const QModelIndex&)"), idx)
    
    def index(self, action):
        """
        Public method to get the index of an action.
        
        @param action reference to the action to get the index for (QAction)
        @return index of the action (QModelIndex)
        """
        if action is None:
            return QModelIndex()
        
        v = action.data()
        if not v.isValid():
            return QModelIndex()
        
        idx = v.toPyObject()
        if not isinstance(idx, QModelIndex):
            return QModelIndex()
        
        return idx
    
    def dragEnterEvent(self, evt):
        """
        Protected method to handle drag enter events.
        
        @param evt reference to the event (QDragEnterEvent)
        """
        if self.__model is not None:
            mimeTypes = self.__model.mimeTypes()
            for mimeType in mimeTypes:
                if evt.mimeData().hasFormat(mimeType):
                    evt.acceptProposedAction()
        
        QMenu.dragEnterEvent(self, evt)
    
    def dropEvent(self, evt):
        """
        Protected method to handle drop events.
        
        @param evt reference to the event (QDropEvent)
        """
        if self.__model is not None:
            act = self.actionAt(evt.pos())
            parentIndex = self.__root
            if act is None:
                row = self.__model.rowCount(self.__root)
            else:
                idx = self.index(act)
                if not idx.isValid():
                    QMenu.dropEvent(self, evt)
                    return
                
                row = idx.row()
                if self.__model.hasChildren(idx):
                    parentIndex = idx
                    row = self.__model.rowCount(idx)
            
            self.__dropRow = row
            self.__dropIndex = parentIndex
            evt.acceptProposedAction()
            self.__model.dropMimeData(evt.mimeData(), evt.dropAction(), 
                                      row, 0, parentIndex)
            self.close()
        
        QMenu.dropEvent(self, evt)
    
    def mousePressEvent(self, evt):
        """
        Protected method handling mouse press events.
        
        @param evt reference to the event object (QMouseEvent)
        """
        if evt.button() == Qt.LeftButton:
            self.__dragStartPosition = evt.pos()
        QMenu.mousePressEvent(self, evt)
    
    def mouseMoveEvent(self, evt):
        """
        Protected method to handle mouse move events.
        
        @param evt reference to the event (QMouseEvent)
        """
        if self.__model is None:
            QMenu.mouseMoveEvent(self, evt)
            return
        
        if not (evt.buttons() & Qt.LeftButton):
            QMenu.mouseMoveEvent(self, evt)
            return
        
        manhattanLength = (evt.pos() - self.__dragStartPosition).manhattanLength()
        if manhattanLength <= QApplication.startDragDistance():
            QMenu.mouseMoveEvent(self, evt)
            return
        
        act = self.actionAt(self.__dragStartPosition)
        if act is None:
            QMenu.mouseMoveEvent(self, evt)
            return
        
        idx = self.index(act)
        if not idx.isValid():
            QMenu.mouseMoveEvent(self, evt)
            return
        
        drag = QDrag(self)
        drag.setMimeData(self.__model.mimeData([idx]))
        actionRect = self.actionGeometry(act)
        drag.setPixmap(QPixmap.grabWidget(self, actionRect))
        
        if drag.exec_() == Qt.MoveAction:
            row = idx.row()
            if self.__dropIndex == idx.parent() and self.__dropRow <= row:
                row += 1
            self.__model.removeRow(row, self.__root)
            
            if not self.isAncestorOf(drag.target()):
                self.close()
            else:
                self.emit(SIGNAL("aboutToShow()"))
    
    def mouseReleaseEvent(self, evt):
        """
        Protected method handling mouse release events.
        
        @param evt reference to the event object (QMouseEvent)
        """
        self._mouseButton = evt.button()
        self._keyboardModifiers = evt.modifiers()
        QMenu.mouseReleaseEvent(self, evt)
    
    def resetFlags(self):
        """
        Public method to reset the saved internal state.
        """
        self._mouseButton = Qt.NoButton
        self._keyboardModifiers = Qt.KeyboardModifiers(Qt.NoModifier)
    
    def removeEntry(self, idx):
        """
        Public method to remove a menu entry.
        
        @param idx index of the entry to be removed (QModelIndex)
        """
        row = idx.row()
        self.__model.removeRow(row, self.__root)
        self.emit(SIGNAL("aboutToShow()"))
