# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a modified QSortFilterProxyModel.
"""

from PyQt4.QtCore import Qt, QModelIndex
from PyQt4.QtGui import QSortFilterProxyModel

class E4TreeSortFilterProxyModel(QSortFilterProxyModel):
    """
    Class implementing a modified QSortFilterProxyModel.
   
    It always accepts the root nodes in the tree so filtering is only done
    on the children.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent object (QObject)
        """
        QSortFilterProxyModel.__init__(self, parent)
        
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
    
    def filterAcceptsRow(self, sourceRow, sourceParent):
        """
        Protected method to determine, if the row is acceptable.
        
        @param sourceRow row number in the source model (integer)
        @param sourceParent index of the source item (QModelIndex)
        @return flag indicating acceptance (boolean)
        """
        idx = self.sourceModel().index(sourceRow, 0, sourceParent)
        if self.sourceModel().hasChildren(idx):
            return True
        
        return QSortFilterProxyModel.filterAcceptsRow(self, sourceRow, sourceParent)
    
    def hasChildren(self, parent = QModelIndex()):
        """
        Public method to check, if a parent node has some children.
        
        @param parent index of the parent node (QModelIndex)
        @return flag indicating the presence of children (boolean)
        """
        sindex = self.mapToSource(parent)
        return self.sourceModel().hasChildren(sindex)
