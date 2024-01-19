# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a model for the AdBlock dialog.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import Helpviewer.HelpWindow

class AdBlockModel(QAbstractItemModel):
    """
    Class implementing a model for the AdBlock dialog.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        QAbstractItemModel.__init__(self, parent)
        
        self.__manager = Helpviewer.HelpWindow.HelpWindow.adblockManager()
        self.connect(self.__manager, SIGNAL("rulesChanged()"), self.__rulesChanged)
    
    def __rulesChanged(self):
        """
        Private slot to handle changes in rules.
        """
        self.reset()
    
    def rule(self, index):
        """
        Public method to get the rule given it's index.
        
        @param index index of the rule (QModelIndex)
        @return reference to the rule (AdBlockRule)
        """
        parent = index.internalPointer()
        return parent.allRules()[index.row()]
    
    def subscription(self, index):
        """
        Public method to get the subscription given it's index.
        
        @param index index of the subscription (QModelIndex)
        @return reference to the subscription (AdBlockSubscription)
        """
        parent = index.internalPointer()
        if parent is not None:
            return None
        row = index.row()
        if row < 0 or row >= len(self.__manager.subscriptions()):
            return None
        return self.__manager.subscriptions()[row]
    
    def subscriptionIndex(self, subscription):
        """
        Public method to get the index of a subscription.
        
        @param subscription reference to the subscription (AdBlockSubscription)
        @return index of the subscription (QModelIndex)
        """
        try:
            row = self.__manager.subscriptions().index(subscription)
            if row < 0 or row >= len(self.__manager.subscriptions()):
                return QModelIndex()
            return self.createIndex(row, 0, 0)
        except ValueError:
            return QModelIndex()
    
    def headerData(self, section, orientation, role = Qt.DisplayRole):
        """
        Public method to get the header data.
        
        @param section section number (integer)
        @param orientation header orientation (Qt.Orientation)
        @param role data role (integer)
        @return header data (QVariant)
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return QVariant(self.trUtf8("Rule"))
        return QAbstractItemModel.headerData(self, section, orientation, role)
    
    def data(self, index, role = Qt.DisplayRole):
        """
        Public method to get data from the model.
        
        @param index index of bookmark to get data for (QModelIndex)
        @param role data role (integer)
        @return bookmark data (QVariant)
        """
        if not index.isValid() or index.model() != self or index.column() != 0:
            return QVariant()
        
        if role in [Qt.EditRole, Qt.DisplayRole]:
            if index.parent().isValid():
                r = self.rule(index)
                return QVariant(r.filter())
            else:
                sub = self.subscription(index)
                if sub is not None:
                    return QVariant(sub.title())
        
        elif role == Qt.CheckStateRole:
            if index.parent().isValid():
                r = self.rule(index)
                if r.isEnabled():
                    return QVariant(Qt.Checked)
                else:
                    return QVariant(Qt.Unchecked)
            else:
                sub = self.subscription(index)
                if sub is not None:
                    if sub.isEnabled():
                        return QVariant(Qt.Checked)
                    else:
                        return QVariant(Qt.Unchecked)
        
        return QVariant()
    
    def columnCount(self, parent = QModelIndex()):
        """
        Public method to get the number of columns.
        
        @param parent index of parent (QModelIndex)
        @return number of columns (integer)
        """
        if parent.column() > 0:
            return 0
        else:
            return 1
    
    def rowCount(self, parent = QModelIndex()):
        """
        Public method to determine the number of rows.
        
        @param parent index of parent (QModelIndex)
        @return number of rows (integer)
        """
        if parent.column() > 0:
            return 0
        
        if not parent.isValid():
            return len(self.__manager.subscriptions())
        
        if parent.internalPointer() is not None:
            return 0
        
        parentNode = self.subscription(parent)
        if parentNode is not None:
            return len(parentNode.allRules())
        
        return 0
    
    def index(self, row, column, parent = QModelIndex()):
        """
        Public method to get a model index for a node cell.
        
        @param row row number (integer)
        @param column column number (integer)
        @param parent index of the parent (QModelIndex)
        @return index (QModelIndex)
        """
        if row < 0 or column < 0 or \
           row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QModelIndex()
        
        if not parent.isValid():
            return self.createIndex(row, column, None)
        
        parentNode = self.subscription(parent)
        return self.createIndex(row, column, parentNode)
    
    def parent(self, index = QModelIndex()):
        """
        Public method to get the index of the parent node.
        
        @param index index of the child node (QModelIndex)
        @return index of the parent node (QModelIndex)
        """
        if not index.isValid():
            return QModelIndex()
        
        parent = index.internalPointer()
        if parent is None:
            return QModelIndex()
        
        parentRow = self.__manager.subscriptions().index(parent)
        return self.createIndex(parentRow, 0, None)
    
    def flags(self, index):
        """
        Public method to get flags for a node cell.
        
        @param index index of the node cell (QModelIndex)
        @return flags (Qt.ItemFlags)
        """
        if not index.isValid():
            return Qt.NoItemFlags
        
        flags = Qt.ItemIsSelectable
        
        if index.parent().isValid():
            flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
            
            parentNode = self.subscription(index.parent())
            if parentNode is not None and parentNode.isEnabled():
                flags |= Qt.ItemIsEnabled
        else:
            flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        
        return flags
    
    def removeRows(self, row, count, parent = QModelIndex()):
        """
        Public method to remove bookmarks from the model.
        
        @param row row of the first bookmark to remove (integer)
        @param count number of bookmarks to remove (integer)
        @param index of the parent bookmark node (QModelIndex)
        @return flag indicating successful removal (boolean)
        """
        if row < 0 or count <= 0 or row + count > self.rowCount(parent):
            return False
        
        if not parent.isValid():
            self.disconnect(self.__manager, SIGNAL("rulesChanged()"), 
                            self.__rulesChanged)
            self.beginRemoveRows(QModelIndex(), row, row + count - 1)
            for subscription in self.__manager.subscriptions()[row:row + count]:
                self.__manager.removeSubscription(subscription)
            self.endRemoveRows()
            self.connect(self.__manager, SIGNAL("rulesChanged()"), 
                         self.__rulesChanged)
            return True
        else:
            sub = self.subscription(parent)
            if sub is not None:
                self.disconnect(self.__manager, SIGNAL("rulesChanged()"), 
                                self.__rulesChanged)
                self.beginRemoveRows(parent, row, row + count - 1)
                for i in reversed(range(row, row + count)):
                    sub.removeRule(i)
                self.endRemoveRows()
                self.connect(self.__manager, SIGNAL("rulesChanged()"), 
                             self.__rulesChanged)
                return True
        
        return False
    
    def setData(self, index, value, role = Qt.EditRole):
        """
        Public method to set the data of a node cell.
        
        @param index index of the node cell (QModelIndex)
        @param value value to be set (QVariant)
        @param role role of the data (integer)
        @return flag indicating success (boolean)
        """
        if not index.isValid() or \
           index.model() != self or \
           index.column() != 0 or \
           (self.flags(index) & Qt.ItemIsEditable) == 0:
            return False
        
        self.disconnect(self.__manager, SIGNAL("rulesChanged()"), self.__rulesChanged)
        changed = False
        
        if role in [Qt.EditRole, Qt.DisplayRole]:
            if index.parent().isValid():
                sub = self.subscription(index.parent())
                if sub is not None:
                    r = self.rule(index)
                    r.setFilter(value.toString())
                    sub.replaceRule(r, index.row())
                    self.emit(SIGNAL("dataChanged(const QModelIndex&, const QModelIndex&)"), 
                        index, index)
                    changed = True
            else:
                sub = self.subscription(index)
                if sub is not None:
                    sub.setTitle(value.toString())
                    self.emit(SIGNAL("dataChanged(const QModelIndex&, const QModelIndex&)"), 
                        index, index)
                    changed = True
        
        elif role == Qt.CheckStateRole:
            if index.parent().isValid():
                sub = self.subscription(index.parent())
                if sub is not None:
                    r = self.rule(index)
                    r.setEnabled(value == Qt.Checked)
                    sub.replaceRule(r, index.row())
                    self.emit(SIGNAL("dataChanged(const QModelIndex&, const QModelIndex&)"), 
                        index, index)
                    changed = True
            else:
                sub = self.subscription(index)
                if sub is not None:
                    sub.setEnabled(value == Qt.Checked)
                    self.emit(SIGNAL("dataChanged(const QModelIndex&, const QModelIndex&)"), 
                        index, index)
                    changed = True
        
        self.connect(self.__manager, SIGNAL("rulesChanged()"), self.__rulesChanged)
        return changed
    
    def hasChildren(self, parent = QModelIndex()):
        """
        Public method to check, if a parent node has some children.
        
        @param parent index of the parent node (QModelIndex)
        @return flag indicating the presence of children (boolean)
        """
        if not parent.isValid():
            return True
        
        if parent.internalPointer() is None:
            return True
        
        return False
