# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a model for search engines.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import QPixmap, QIcon

class OpenSearchEngineModel(QAbstractTableModel):
    """
    Class implementing a model for search engines.
    """
    def __init__(self, manager, parent = None):
        """
        Constructor
        
        @param manager reference to the search engine manager (OpenSearchManager)
        @param parent reference to the parent object (QObject)
        """
        QAbstractTableModel.__init__(self, parent)
        
        self.__manager = manager
        self.connect(manager, SIGNAL("changed()"), self.__enginesChanged)
        
        self.__headers = [
            self.trUtf8("Name"), 
            self.trUtf8("Keywords"), 
        ]
    
    def removeRows(self, row, count, parent = QModelIndex()):
        """
        Public method to remove entries from the model.
        
        @param row start row (integer)
        @param count number of rows to remove (integer)
        @param parent parent index (QModelIndex)
        @return flag indicating success (boolean)
        """
        if parent.isValid():
            return False
        
        if count <= 0:
            return False
        
        if self.rowCount() <= 1:
            return False
        
        lastRow = row + count - 1
        
        self.beginRemoveRows(parent, row, lastRow)
        
        nameList = self.__manager.allEnginesNames()
        for index in range(row, lastRow + 1):
            self.__manager.removeEngine(nameList[index])
        
        # removeEngine emits changed()
        #self.endRemoveRows()
        
        return True
    
    def rowCount(self, parent = QModelIndex()):
        """
        Public method to get the number of rows of the model.
        
        @param parent parent index (QModelIndex)
        @return number of rows (integer)
        """
        if parent.isValid():
            return 0
        else:
            return self.__manager.enginesCount()
    
    def columnCount(self, parent = QModelIndex()):
        """
        Public method to get the number of columns of the model.
        
        @param parent parent index (QModelIndex)
        @return number of columns (integer)
        """
        return 2
    
    def flags(self, index):
        """
        Public method to get flags for a model cell.
        
        @param index index of the model cell (QModelIndex)
        @return flags (Qt.ItemFlags)
        """
        if index.column() == 1:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def data(self, index, role):
        """
        Public method to get data from the model.
        
        @param index index to get data for (QModelIndex)
        @param role role of the data to retrieve (integer)
        @return requested data (QVariant)
        """
        if index.row() >= self.__manager.enginesCount() or index.row() < 0:
            return QVariant()
        
        engine = self.__manager.engine(self.__manager.allEnginesNames()[index.row()])
        
        if engine is None:
            return QVariant()
        
        if index.column() == 0:
            if role == Qt.DisplayRole:
                return QVariant(engine.name())
                
            elif role == Qt.DecorationRole:
                image = engine.image()
                if image.isNull():
                    from Helpviewer.HelpWindow import HelpWindow
                    icon = HelpWindow.icon(QUrl(engine.imageUrl()))
                else:
                    icon = QIcon(QPixmap.fromImage(image))
                return QVariant(icon)
                
            elif role == Qt.ToolTipRole:
                description = self.trUtf8("<strong>Description:</strong> %1")\
                              .arg(engine.description())
                if engine.providesSuggestions():
                    description.append("<br/>")
                    description.append(
                        self.trUtf8("<strong>Provides contextual suggestions</strong>"))
                
                return QVariant(description)
        elif index.column() == 1:
            if role in [Qt.EditRole, Qt.DisplayRole]:
                return QVariant(
                    QStringList(self.__manager.keywordsForEngine(engine)).join(","))
            elif role == Qt.ToolTipRole:
                return QVariant(self.trUtf8("Comma-separated list of keywords that may"
                    " be entered in the location bar followed by search terms to search"
                    " with this engine"))
        
        return QVariant()
    
    def setData(self, index, value, role = Qt.EditRole):
        """
        Public method to set the data of a model cell.
        
        @param index index of the model cell (QModelIndex)
        @param value value to be set (QVariant)
        @param role role of the data (integer)
        @return flag indicating success (boolean)
        """
        if not index.isValid() or index.column() != 1:
            return False
        
        if index.row() >= self.rowCount() or index.row() < 0:
            return False
        
        if role != Qt.EditRole:
            return False
        
        engineName = self.__manager.allEnginesNames()[index.row()]
        keywords = value.toString().split(QRegExp("[ ,]+"), QString.SkipEmptyParts)
        self.__manager.setKeywordsForEngine(self.__manager.engine(engineName), keywords)
        
        return True
    
    def headerData(self, section, orientation, role = Qt.DisplayRole):
        """
        Public method to get the header data.
        
        @param section section number (integer)
        @param orientation header orientation (Qt.Orientation)
        @param role data role (integer)
        @return header data (QVariant)
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return QVariant(self.__headers[section])
            except IndexError:
                pass
        
        return QVariant()
    
    def __enginesChanged(self):
        """
        Private slot handling a change of the registered engines.
        """
        QAbstractTableModel.reset(self)
