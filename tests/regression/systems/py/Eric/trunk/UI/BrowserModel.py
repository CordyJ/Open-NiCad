# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the browser model.
"""

import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import Utilities.ClassBrowsers
import Utilities.ClassBrowsers.ClbrBaseClasses

import UI.PixmapCache
import Preferences
import Utilities

BrowserItemRoot       = 0
BrowserItemDirectory  = 1
BrowserItemSysPath    = 2
BrowserItemFile       = 3
BrowserItemClass      = 4
BrowserItemMethod     = 5
BrowserItemAttributes = 6
BrowserItemAttribute  = 7
BrowserItemCoding     = 8

class BrowserModel(QAbstractItemModel):
    """
    Class implementing the browser model.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to parent object (QObject)
        """
        QAbstractItemModel.__init__(self, parent)
        
        rootData = QVariant(QApplication.translate("BrowserModel", "Name"))
        self.rootItem = BrowserItem(None, rootData)
        
        self.progDir = None
        
        self.__populateModel()
    
    def columnCount(self, parent=QModelIndex()):
        """
        Public method to get the number of columns.
        
        @param parent index of parent item (QModelIndex)
        @return number of columns (integer)
        """
        if parent.isValid():
            item = parent.internalPointer()
        else:
            item = self.rootItem
        
        return item.columnCount() + 1
    
    def data(self, index, role):
        """
        Public method to get data of an item.
        
        @param index index of the data to retrieve (QModelIndex)
        @param role role of data (Qt.ItemDataRole)
        @return requested data (QVariant)
        """
        if not index.isValid():
            return QVariant()
        
        if role == Qt.DisplayRole:
            item = index.internalPointer()
            if index.column() < item.columnCount():
                return QVariant(item.data(index.column()))
            elif index.column() == item.columnCount() and \
                 index.column() < self.columnCount(self.parent(index)):
                # This is for the case where an item under a multi-column parent
                # doesn't have a value for all the columns
                return QVariant("")
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                return QVariant(index.internalPointer().getIcon())
        
        return QVariant()
    
    def flags(self, index):
        """
        Public method to get the item flags.
        
        @param index index of the data to retrieve (QModelIndex)
        @return requested flags (Qt.ItemFlags)
        """
        if not index.isValid():
            return Qt.ItemIsEnabled
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def headerData(self, section, orientation, role = Qt.DisplayRole):
        """
        Public method to get the header data.
        
        @param section number of section to get data for (integer)
        @param orientation header orientation (Qt.Orientation)
        @param role role of data (Qt.ItemDataRole)
        @return requested header data (QVariant)
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section >= self.rootItem.columnCount():
                return QVariant("")
            else:
                return self.rootItem.data(section)
        
        return QVariant()
    
    def index(self, row, column, parent = QModelIndex()):
        """
        Public method to create an index.
        
        @param row row number of the new index (integer)
        @param column column number of the new index (integer)
        @param parent index of parent item (QModelIndex)
        @return index object (QModelIndex)
        """
        # The model/view framework considers negative values out-of-bounds, 
        # however in python they work when indexing into lists. So make sure 
        # we return an invalid index for out-of-bounds row/col
        if row < 0 or column < 0 or \
           row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QModelIndex()
        
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        
        try:
            if not parentItem.isPopulated():
                self.populateItem(parentItem)
            childItem = parentItem.child(row)
        except IndexError:
            childItem = None
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()
    
    def parent(self, index):
        """
        Public method to get the index of the parent object.
        
        @param index index of the item (QModelIndex)
        @return index of parent item (QModelIndex)
        """
        if not index.isValid():
            return QModelIndex()
        
        childItem = index.internalPointer()
        parentItem = childItem.parent()
        
        if parentItem == self.rootItem:
            return QModelIndex()
        
        return self.createIndex(parentItem.row(), 0, parentItem)
    
    def rowCount(self, parent = QModelIndex()):
        """
        Public method to get the number of rows.
        
        @param parent index of parent item (QModelIndex)
        @return number of rows (integer)
        """
        # Only the first column should have children
        if parent.column() > 0:
            return 0
        
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
            if not parentItem.isPopulated():    # lazy population
                self.populateItem(parentItem)
        
        return parentItem.childCount()

    def hasChildren(self, parent = QModelIndex()):
        """
        Public method to check for the presence of child items.
        
        We always return True for normal items in order to do lazy
        population of the tree.
        
        @param parent index of parent item (QModelIndex)
        @return flag indicating the presence of child items (boolean)
        """
        # Only the first column should have children
        if parent.column() > 0:
            return 0
        
        if not parent.isValid():
            return self.rootItem.childCount() > 0
        
        if parent.internalPointer().isLazyPopulated():
            return True
        else:
            return parent.internalPointer().childCount() > 0

    def clear(self):
        """
        Public method to clear the model.
        """
        self.rootItem.removeChildren()
        self.reset()
    
    def item(self, index):
        """
        Public method to get a reference to an item.
        
        @param index index of the data to retrieve (QModelIndex)
        @return requested item reference (BrowserItem)
        """
        if not index.isValid():
            return None
        
        return index.internalPointer()
    
    def __populateModel(self):
        """
        Private method to populate the browser model.
        """
        self._addItem(BrowserSysPathItem(self.rootItem), self.rootItem)
        
        self.toplevelDirs = QStringList()
        tdp = Preferences.Prefs.settings.value('BrowserModel/ToplevelDirs').toStringList()
        if not tdp.isEmpty():
            self.toplevelDirs = tdp
        else:
            self.toplevelDirs.append(Utilities.toNativeSeparators(QDir.homePath()))
            for d in QDir.drives():
                self.toplevelDirs.append(Utilities.toNativeSeparators(\
                    d.absoluteFilePath()))
        
        for d in self.toplevelDirs:
            self._addItem(BrowserDirectoryItem(self.rootItem, d), self.rootItem)
    
    def programChange(self, dirname):
        """
        Public method to change the entry for the directory of file being debugged.
        
        @param dirname name of the directory containg the file (string or QString)
        """
        if self.progDir:
            if dirname == self.progDir.dirName():
                return
            
            # remove old entry
            self.beginRemoveRows(QModelIndex(), self.progDir.row(), self.progDir.row())
            self.rootItem.removeChild(self.progDir)
            self.endRemoveRows()
            self.progDir = None
        
        itm = BrowserDirectoryItem(self.rootItem, dirname)
        self.addItem(itm)
        self.progDir = itm
    
    def addTopLevelDir(self, dirname):
        """
        Public method to add a new toplevel directory.
        
        @param dirname name of the new toplevel directory (string or QString)
        """
        if not self.toplevelDirs.contains(dirname):
            itm = BrowserDirectoryItem(self.rootItem, dirname)
            self.addItem(itm)
            self.toplevelDirs.append(itm.dirName())
    
    def removeToplevelDir(self, index):
        """
        Public method to remove a toplevel directory.
        
        @param index index of the toplevel directory to be removed (QModelIndex)
        """
        if not index.isValid():
            return
        
        item = index.internalPointer()
        self.beginRemoveRows(index.parent(), index.row(), index.row())
        self.rootItem.removeChild(item)
        self.endRemoveRows()
        
        self.toplevelDirs.removeAll(item.dirName())
    
    def saveToplevelDirs(self):
        """
        Public slot to save the toplevel directories.
        """
        Preferences.Prefs.settings.setValue('BrowserModel/ToplevelDirs', 
            QVariant(self.toplevelDirs))
    
    def _addItem(self, itm, parentItem):
        """
        Protected slot to add an item.
        
        @param itm reference to item to add (BrowserItem)
        @param parentItem reference to item to add to (BrowserItem)
        """
        parentItem.appendChild(itm)
    
    def addItem(self, itm, parent = QModelIndex()):
        """
        Puplic slot to add an item.
        
        @param itm item to add (BrowserItem)
        @param parent index of parent item (QModelIndex)
        """
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        
        cnt = parentItem.childCount()
        self.beginInsertRows(parent, cnt, cnt)
        self._addItem(itm, parentItem)
        self.endInsertRows()

    def populateItem(self, parentItem, repopulate = False):
        """
        Public method to populate an item's subtree.
        
        @param parentItem reference to the item to be populated
        @param repopulate flag indicating a repopulation (boolean)
        """
        if parentItem.type() == BrowserItemDirectory:
            self.populateDirectoryItem(parentItem, repopulate)
        elif parentItem.type() == BrowserItemSysPath:
            self.populateSysPathItem(parentItem, repopulate)
        elif parentItem.type() == BrowserItemFile:
            self.populateFileItem(parentItem, repopulate)
        elif parentItem.type() == BrowserItemClass:
            self.populateClassItem(parentItem, repopulate)
        elif parentItem.type() == BrowserItemMethod:
            self.populateMethodItem(parentItem, repopulate)
        elif parentItem.type() == BrowserItemAttributes:
            self.populateClassAttributesItem(parentItem, repopulate)

    def populateDirectoryItem(self, parentItem, repopulate = False):
        """
        Public method to populate a directory item's subtree.
        
        @param parentItem reference to the directory item to be populated
        @param repopulate flag indicating a repopulation (boolean)
        """
        qdir = QDir(parentItem.dirName())
        
        entryInfoList = \
            qdir.entryInfoList(QDir.Filters(QDir.AllEntries | QDir.NoDotAndDotDot))
        if len(entryInfoList) > 0:
            if repopulate:
                self.beginInsertRows(self.createIndex(parentItem.row(), 0, parentItem),
                    0, len(entryInfoList) - 1)
            for f in entryInfoList:
                if f.isDir():
                    node = BrowserDirectoryItem(parentItem,
                        unicode(Utilities.toNativeSeparators(f.absoluteFilePath())), 
                        False)
                else:
                    node = BrowserFileItem(parentItem,
                        unicode(Utilities.toNativeSeparators(f.absoluteFilePath())))
                self._addItem(node, parentItem)
            if repopulate:
                self.endInsertRows()

    def populateSysPathItem(self, parentItem, repopulate = False):
        """
        Public method to populate a sys.path item's subtree.
        
        @param parentItem reference to the sys.path item to be populated
        @param repopulate flag indicating a repopulation (boolean)
        """
        if len(sys.path) > 0:
            if repopulate:
                self.beginInsertRows(self.createIndex(parentItem.row(), 0, parentItem),
                    0, len(sys.path) - 1)
            for p in sys.path:
                if p == '':
                    p = os.getcwd()
                
                node = BrowserDirectoryItem(parentItem, p)
                self._addItem(node, parentItem)
            if repopulate:
                self.endInsertRows()

    def populateFileItem(self, parentItem, repopulate = False):
        """
        Public method to populate a file item's subtree.
        
        @param parentItem reference to the file item to be populated
        @param repopulate flag indicating a repopulation (boolean)
        """
        moduleName = parentItem.moduleName()
        fileName = parentItem.fileName()
        try:
            dict = Utilities.ClassBrowsers.readmodule(\
                moduleName, [parentItem.dirName()], 
                parentItem.isPythonFile() or parentItem.isPython3File())
        except ImportError:
            return
        
        keys = dict.keys()
        if len(keys) > 0:
            if repopulate:
                self.beginInsertRows(self.createIndex(parentItem.row(), 0, parentItem),
                    0, len(keys) - 1)
            for key in keys:
                if key.startswith("@@"):
                    # special treatment done later
                    continue
                cl = dict[key]
                try:
                    if cl.module == moduleName:
                        node = BrowserClassItem(parentItem, cl, fileName)
                        self._addItem(node, parentItem)
                except AttributeError:
                    pass
            if "@@Coding@@" in keys:
                node = BrowserCodingItem(parentItem, 
                    QApplication.translate("BrowserModel", "Coding: %1")\
                        .arg(dict["@@Coding@@"].coding))
                self._addItem(node, parentItem)
            if "@@Globals@@" in keys:
                node = BrowserClassAttributesItem(parentItem, 
                    dict["@@Globals@@"].globals, 
                    QApplication.translate("BrowserModel", "Globals"))
                self._addItem(node, parentItem)
            if repopulate:
                self.endInsertRows()

    def populateClassItem(self, parentItem, repopulate = False):
        """
        Public method to populate a class item's subtree.
        
        @param parentItem reference to the class item to be populated
        @param repopulate flag indicating a repopulation (boolean)
        """
        cl = parentItem.classObject()
        file_ = parentItem.fileName()
        
        if cl is None:
            return
        
        # build sorted list of names
        keys = []
        for name in cl.classes.keys():
            keys.append((name, 'c'))
        for name in cl.methods.keys():
            keys.append((name, 'm'))
        
        if len(keys) > 0:
            if repopulate:
                self.beginInsertRows(self.createIndex(parentItem.row(), 0, parentItem),
                    0, len(keys) - 1)
            for key, kind in keys:
                if kind == 'c':
                    node = BrowserClassItem(parentItem, cl.classes[key], file_)
                elif kind == 'm':
                    node = BrowserMethodItem(parentItem, cl.methods[key], file_)
                self._addItem(node, parentItem)
            if repopulate:
                self.endInsertRows()
        
        if len(cl.attributes):
            node = BrowserClassAttributesItem(\
                parentItem, cl.attributes, 
                QApplication.translate("BrowserModel", "Attributes"))
            if repopulate:
                self.addItem(node, 
                    self.createIndex(parentItem.row(), 0, parentItem))
            else:
                self._addItem(node, parentItem)
        
        if len(cl.globals):
            node = BrowserClassAttributesItem(\
                parentItem, cl.globals, 
                QApplication.translate("BrowserModel", "Attributes (global)"))
            if repopulate:
                self.addItem(node, 
                    self.createIndex(parentItem.row(), 0, parentItem))
            else:
                self._addItem(node, parentItem)

    def populateMethodItem(self, parentItem, repopulate = False):
        """
        Public method to populate a method item's subtree.
        
        @param parentItem reference to the method item to be populated
        @param repopulate flag indicating a repopulation (boolean)
        """
        fn = parentItem.functionObject()
        file_ = parentItem.fileName()
        
        if fn is None:
            return
        
        # build sorted list of names
        keys = []
        for name in fn.classes.keys():
            keys.append((name, 'c'))
        for name in fn.methods.keys():
            keys.append((name, 'm'))
        
        if len(keys) > 0:
            if repopulate:
                self.beginInsertRows(self.createIndex(parentItem.row(), 0, parentItem),
                    0, len(keys) - 1)
            for key, kind in keys:
                if kind == 'c':
                    node = BrowserClassItem(parentItem, fn.classes[key], file_)
                elif kind == 'm':
                    node = BrowserMethodItem(parentItem, fn.methods[key], file_)
                self._addItem(node, parentItem)
            if repopulate:
                self.endInsertRows()

    def populateClassAttributesItem(self, parentItem, repopulate = False):
        """
        Public method to populate a class attributes item's subtree.
        
        @param parentItem reference to the class attributes item to be populated
        @param repopulate flag indicating a repopulation (boolean)
        """
        attributes = parentItem.attributes()
        if not attributes:
            return
        
        keys = attributes.keys()
        if len(keys) > 0:
            if repopulate:
                self.beginInsertRows(self.createIndex(parentItem.row(), 0, parentItem),
                    0, len(keys) - 1)
            for key in keys:
                node = BrowserClassAttributeItem(parentItem, attributes[key])
                self._addItem(node, parentItem)
            if repopulate:
                self.endInsertRows()

class BrowserItem(object):
    """
    Class implementing the data structure for browser items.
    """
    def __init__(self, parent, data):
        """
        Constructor.
        
        @param parent reference to the parent item
        @param data single data of the item
        """
        self.childItems = []
        
        self.parentItem = parent
        self.itemData = [data]
        self.type_ = BrowserItemRoot
        self.icon = UI.PixmapCache.getIcon("empty.png")
        self._populated = True
        self._lazyPopulation = False
    
    def appendChild(self, child):
        """
        Public method to add a child to this item.
        
        @param child reference to the child item to add (BrowserItem)
        """
        self.childItems.append(child)
        self._populated = True
    
    def removeChild(self, child):
        """
        Public method to remove a child.
        
        @param child reference to the child to remove (BrowserItem)
        """
        self.childItems.remove(child)
    
    def removeChildren(self):
        """
        Public method to remove all children.
        """
        self.childItems = []
    
    def child(self, row):
        """
        Public method to get a child id.
        
        @param row number of child to get the id of (integer)
        @param return reference to the child item (BrowserItem)
        """
        return self.childItems[row]
    
    def children(self):
        """
        Public method to get the ids of all child items.
        
        @return references to all child items (list of BrowserItem)
        """
        return self.childItems[:]
    
    def childCount(self):
        """
        Public method to get the number of available child items.
        
        @return number of child items (integer)
        """
        return len(self.childItems)
    
    def columnCount(self):
        """
        Public method to get the number of available data items.
        
        @return number of data items (integer)
        """
        return len(self.itemData)
    
    def data(self, column):
        """
        Public method to get a specific data item.
        
        @param column number of the requested data item (integer)
        @param return the stored data item
        """
        try:
            return self.itemData[column]
        except IndexError:
            return ""
    
    def parent(self):
        """
        Public method to get the reference to the parent item.
        
        @return reference to the parent item
        """
        return self.parentItem
    
    def row(self):
        """
        Public method to get the row number of this item.
        
        @return row number (integer)
        """
        return self.parentItem.childItems.index(self)
    
    def type(self):
        """
        Public method to get the item type.
        
        @return type of the item
        """
        return self.type_
    
    def isPublic(self):
        """
        Public method returning the public visibility status.
        
        @return flag indicating public visibility (boolean)
        """
        return True
    
    def getIcon(self):
        """
        Public method to get the items icon.
        
        @return the icon (QIcon)
        """
        return self.icon
    
    def isPopulated(self):
        """
        Public method to chek, if this item is populated.
        
        @return population status (boolean)
        """
        return self._populated
    
    def isLazyPopulated(self):
        """
        Public method to check, if this item should be populated lazyly.
        
        @return lazy population flag (boolean)
        """
        return self._lazyPopulation
    
    def lessThan(self, other, column, order):
        """
        Public method to check, if the item is less than the other one.
        
        @param other reference to item to compare against (BrowserItem)
        @param column column number to use for the comparison (integer)
        @param order sort order (Qt.SortOrder) (for special sorting)
        @return true, if this item is less than other (boolean)
        """
        try:
            return self.itemData[column] < other.itemData[column]
        except IndexError:
            return False

class BrowserDirectoryItem(BrowserItem):
    """
    Class implementing the data structure for browser directory items.
    """
    def __init__(self, parent, dinfo, full = True):
        """
        Constructor
        
        @param parent parent item
        @param dinfo dinfo is the string for the directory (string or QString)
        @param full flag indicating full pathname should be displayed (boolean)
        """
        self._dirName = os.path.abspath(unicode(dinfo))
        
        if full:
            dn = self._dirName
        else:
            dn = os.path.basename(self._dirName)
        
        BrowserItem.__init__(self, parent, dn)
        
        self.type_ = BrowserItemDirectory
        self.icon = UI.PixmapCache.getIcon("dirClosed.png")
        self._populated = False
        self._lazyPopulation = True
    
    def setName(self, dinfo, full = True):
        """
        Public method to set the directory name.
        
        @param dinfo dinfo is the string for the directory (string or QString)
        @param full flag indicating full pathname should be displayed (boolean)
        """
        self._dirName = os.path.abspath(unicode(dinfo))
        
        if full:
            dn = self._dirName
        else:
            dn = os.path.basename(self._dirName)
        self.itemData[0] = dn
    
    def dirName(self):
        """
        Public method returning the directory name.
        
        @return directory name (string)
        """
        return self._dirName
    
    def lessThan(self, other, column, order):
        """
        Public method to check, if the item is less than the other one.
        
        @param other reference to item to compare against (BrowserItem)
        @param column column number to use for the comparison (integer)
        @param order sort order (Qt.SortOrder) (for special sorting)
        @return true, if this item is less than other (boolean)
        """
        if issubclass(other.__class__, BrowserFileItem):
            if Preferences.getUI("BrowsersListFoldersFirst"):
                return order == Qt.AscendingOrder
        
        return BrowserItem.lessThan(self, other, column, order)

class BrowserSysPathItem(BrowserItem):
    """
    Class implementing the data structure for browser sys.path items.
    """
    def __init__(self, parent):
        """
        Constructor
        
        @param parent parent item
        """
        BrowserItem.__init__(self, parent, "sys.path")
        
        self.type_ = BrowserItemSysPath
        self.icon = UI.PixmapCache.getIcon("filePython.png")
        self._populated = False
        self._lazyPopulation = True

class BrowserFileItem(BrowserItem):
    """
    Class implementing the data structure for browser file items.
    """
    def __init__(self, parent, finfo, full = True, sourceLanguage = ""):
        """
        Constructor
        
        @param parent parent item
        @param finfo the string for the file (string)
        @param full flag indicating full pathname should be displayed (boolean)
        @param sourceLanguage source code language of the project (string)
        """
        BrowserItem.__init__(self, parent, os.path.basename(finfo))
        
        self.type_ = BrowserItemFile
        if finfo.endswith('.ui.h'):
            self.fileext = '.ui.h'
        else:
            self.fileext = os.path.splitext(finfo)[1].lower()
        self._filename = os.path.abspath(finfo)
        self._dirName = os.path.dirname(finfo)
        self.sourceLanguage = sourceLanguage
        
        self._moduleName = ''
        
        if self.isPythonFile():
            if self.fileext == '.py':
                self.icon = UI.PixmapCache.getIcon("filePython.png")
            else:
                self.icon = UI.PixmapCache.getIcon("filePython2.png")
            self._populated = False
            self._lazyPopulation = True
            self._moduleName = os.path.basename(finfo)
        elif self.isPython3File():
            self.icon = UI.PixmapCache.getIcon("filePython.png")
            self._populated = False
            self._lazyPopulation = True
            self._moduleName = os.path.basename(finfo)
        elif self.isRubyFile():
            self.icon = UI.PixmapCache.getIcon("fileRuby.png")
            self._populated = False
            self._lazyPopulation = True
            self._moduleName = os.path.basename(finfo)
        elif self.isDesignerFile() or self.isDesignerHeaderFile():
            self.icon = UI.PixmapCache.getIcon("fileDesigner.png")
        elif self.isLinguistFile():
            if self.fileext == '.ts':
                self.icon = UI.PixmapCache.getIcon("fileLinguist.png")
            else:
                self.icon = UI.PixmapCache.getIcon("fileLinguist2.png")
        elif self.isResourcesFile():
            self.icon = UI.PixmapCache.getIcon("fileResource.png")
        elif self.isProjectFile():
            self.icon = UI.PixmapCache.getIcon("fileProject.png")
        elif self.isMultiProjectFile():
            self.icon = UI.PixmapCache.getIcon("fileMultiProject.png")
        elif self.isIdlFile():
            self.icon = UI.PixmapCache.getIcon("fileIDL.png")
            self._populated = False
            self._lazyPopulation = True
            self._moduleName = os.path.basename(finfo)
        elif self.isPixmapFile():
            self.icon = UI.PixmapCache.getIcon("filePixmap.png")
        elif self.isSvgFile():
            self.icon = UI.PixmapCache.getIcon("fileSvg.png")
        elif self.isDFile():
            self.icon = UI.PixmapCache.getIcon("fileD.png")
        else:
            self.icon = UI.PixmapCache.getIcon("fileMisc.png")
    
    def setName(self, finfo, full = True):
        """
        Public method to set the directory name.
        
        @param finfo the string for the file (string)
        @param full flag indicating full pathname should be displayed (boolean)
        """
        self._filename = os.path.abspath(finfo)
        self.itemData[0] = os.path.basename(finfo)
        if self.isPythonFile() or self.isPython3File() or \
           self.isRubyFile() or self.isIdlFile():
            self._dirName = os.path.dirname(finfo)
            self._moduleName = os.path.basename(finfo)
    
    def fileName(self):
        """
        Public method returning the filename.
        
        @return filename (string)
        """
        return self._filename
    
    def fileExt(self):
        """
        Public method returning the file extension.
        
        @return file extension (string)
        """
        return self.fileext
    
    def dirName(self):
        """
        Public method returning the directory name.
        
        @return directory name (string)
        """
        return self._dirName
    
    def moduleName(self):
        """
        Public method returning the module name.
        
        @return module name (string)
        """
        return self._moduleName
    
    def isPythonFile(self):
        """
        Public method to check, if this file is a Python script.
        
        @return flag indicating a Python file (boolean)
        """
        return self.fileext in Preferences.getPython("PythonExtensions") or \
               (self.fileext == "" and self.sourceLanguage == "Python")
    
    def isPython3File(self):
        """
        Public method to check, if this file is a Python3 script.
        
        @return flag indicating a Python file (boolean)
        """
        return self.fileext in Preferences.getPython("Python3Extensions") or \
               (self.fileext == "" and self.sourceLanguage == "Python3")
    
    def isRubyFile(self):
        """
        Public method to check, if this file is a Ruby script.
        
        @return flag indicating a Ruby file (boolean)
        """
        return self.fileext == '.rb' or \
               (self.fileext == "" and self.sourceLanguage == "Ruby")
    
    def isDesignerFile(self):
        """
        Public method to check, if this file is a Qt-Designer file.
        
        @return flag indicating a Qt-Designer file (boolean)
        """
        return self.fileext == '.ui'
    
    def isDesignerHeaderFile(self):
        """
        Public method to check, if this file is a Qt-Designer header file.
        
        @return flag indicating a Qt-Designer header file (boolean)
        """
        return self.fileext == '.ui.h'
    
    def isLinguistFile(self):
        """
        Public method to check, if this file is a Qt-Linguist file.
        
        @return flag indicating a Qt-Linguist file (boolean)
        """
        return self.fileext in ['.ts', '.qm']
    
    def isResourcesFile(self):
        """
        Public method to check, if this file is a Qt-Resources file.
        
        @return flag indicating a Qt-Resources file (boolean)
        """
        return self.fileext == '.qrc'
    
    def isProjectFile(self):
        """
        Public method to check, if this file is an eric4 project file.
        
        @return flag indicating an eric4 project file (boolean)
        """
        return self.fileext in ['.e3p', '.e3pz', '.e4p', '.e4pz']
    
    def isMultiProjectFile(self):
        """
        Public method to check, if this file is an eric4 multi project file.
        
        @return flag indicating an eric4 project file (boolean)
        """
        return self.fileext in ['.e4m', '.e4mz']
    
    def isIdlFile(self):
        """
        Public method to check, if this file is a CORBA IDL file.
        
        @return flag indicating a CORBA IDL file (boolean)
        """
        return self.fileext == '.idl'
    
    def isPixmapFile(self):
        """
        Public method to check, if this file is a pixmap file.
        
        @return flag indicating a pixmap file (boolean)
        """
        return self.fileext[1:] in QImageReader.supportedImageFormats()
    
    def isSvgFile(self):
        """
        Public method to check, if this file is a SVG file.
        
        @return flag indicating a SVG file (boolean)
        """
        return self.fileext == '.svg'
    
    def isDFile(self):
        """
        Public method to check, if this file is a D file.
        
        @return flag indicating a D file (boolean)
        """
        return self.fileext in ['.d', '.di'] or \
               (self.fileext == "" and self.sourceLanguage == "D")
    
    def lessThan(self, other, column, order):
        """
        Public method to check, if the item is less than the other one.
        
        @param other reference to item to compare against (BrowserItem)
        @param column column number to use for the comparison (integer)
        @param order sort order (Qt.SortOrder) (for special sorting)
        @return true, if this item is less than other (boolean)
        """
        if not issubclass(other.__class__, BrowserFileItem):
            if Preferences.getUI("BrowsersListFoldersFirst"):
                return order == Qt.DescendingOrder
        
        if issubclass(other.__class__, BrowserFileItem):
            sinit = os.path.basename(self._filename).startswith('__init__.py')
            oinit = os.path.basename(other.fileName()).startswith('__init__.py')
            if sinit and not oinit:
                return order == Qt.AscendingOrder
            if not sinit and oinit:
                return order == Qt.DescendingOrder
        
        return BrowserItem.lessThan(self, other, column, order)

class BrowserClassItem(BrowserItem):
    """
    Class implementing the data structure for browser class items.
    """
    def __init__(self, parent, cl, filename):
        """
        Constructor
        
        @param parent parent item
        @param cl Class object to be shown
        @param filename filename of the file defining this class
        """
        name = cl.name
        if hasattr(cl, 'super') and cl.super:
            supers = []
            for sup in cl.super:
                try:
                    sname = sup.name
                    if sup.module != cl.module:
                        sname = "%s.%s" % (sup.module, sname)
                except AttributeError:
                    sname = sup
                supers.append(sname)
            name = name + "(%s)" % ", ".join(supers)
        
        BrowserItem.__init__(self, parent, name)
        
        self.type_ = BrowserItemClass
        self.name = name
        self._classObject = cl
        self._filename = filename
        
        self.isfunction = isinstance(self._classObject, 
                                     Utilities.ClassBrowsers.ClbrBaseClasses.Function)
        self.ismodule = isinstance(self._classObject, 
                                   Utilities.ClassBrowsers.ClbrBaseClasses.Module)
        if self.isfunction:
            if cl.isPrivate():
                self.icon = UI.PixmapCache.getIcon("method_private.png")
            elif cl.isProtected():
                self.icon = UI.PixmapCache.getIcon("method_protected.png")
            else:
                self.icon = UI.PixmapCache.getIcon("method.png")
            self.itemData[0] = "%s(%s)" % (name, ", ".join(self._classObject.parameters))
            # if no defaults are wanted
            # ... % (name, ", ".join([e.split('=')[0].strip() \
            #                        for e in self._classObject.parameters]))
        elif self.ismodule:
            self.icon = UI.PixmapCache.getIcon("module.png")
        else:
            if cl.isPrivate():
                self.icon = UI.PixmapCache.getIcon("class_private.png")
            elif cl.isProtected():
                self.icon = UI.PixmapCache.getIcon("class_protected.png")
            else:
                self.icon = UI.PixmapCache.getIcon("class.png")
        if self._classObject and \
           (self._classObject.methods or \
            self._classObject.classes or \
            self._classObject.attributes):
            self._populated = False
            self._lazyPopulation = True
    
    def fileName(self):
        """
        Public method returning the filename.
        
        @return filename (string)
        """
        return self._filename
    
    def classObject(self):
        """
        Public method returning the class object.
        
        @return reference to the class object
        """
        return self._classObject
    
    def lineno(self):
        """
        Public method returning the line number defining this object.
        
        return line number defining the object (integer)
        """
        return self._classObject.lineno
    
    def lessThan(self, other, column, order):
        """
        Public method to check, if the item is less than the other one.
        
        @param other reference to item to compare against (BrowserItem)
        @param column column number to use for the comparison (integer)
        @param order sort order (Qt.SortOrder) (for special sorting)
        @return true, if this item is less than other (boolean)
        """
        if issubclass(other.__class__, BrowserCodingItem) or \
           issubclass(other.__class__, BrowserClassAttributesItem):
            return order == Qt.DescendingOrder
        
        if Preferences.getUI("BrowsersListContentsByOccurrence") and column == 0:
            if order == Qt.AscendingOrder:
                return self.lineno() < other.lineno()
            else:
                return self.lineno() > other.lineno()
        
        return BrowserItem.lessThan(self, other, column, order)
    
    def isPublic(self):
        """
        Public method returning the public visibility status.
        
        @return flag indicating public visibility (boolean)
        """
        return self._classObject.isPublic()

class BrowserMethodItem(BrowserItem):
    """
    Class implementing the data structure for browser method items.
    """
    def __init__(self, parent, fn, filename):
        """
        Constructor
        
        @param parent parent item
        @param fn Function object to be shown
        @param filename filename of the file defining this class
        """
        name = fn.name
        BrowserItem.__init__(self, parent, name)
        
        self.type_ = BrowserItemMethod
        self.name = name
        self._functionObject = fn
        self._filename = filename
        if self._functionObject.isPrivate():
            self.icon = UI.PixmapCache.getIcon("method_private.png")
        elif self._functionObject.isProtected():
            self.icon = UI.PixmapCache.getIcon("method_protected.png")
        else:
            self.icon = UI.PixmapCache.getIcon("method.png")
        self.itemData[0] =  "%s(%s)" % \
            (name, ", ".join(self._functionObject.parameters))
        # if no defaults are wanted
        # ... % (name, ", ".join(\
        #       [e.split('=')[0].strip() for e in self._functionObject.parameters]))
        if self._functionObject and \
           (self._functionObject.methods or self._functionObject.classes):
            self._populated = False
            self._lazyPopulation = True
    
    def fileName(self):
        """
        Public method returning the filename.
        
        @return filename (string)
        """
        return self._filename
    
    def functionObject(self):
        """
        Public method returning the function object.
        
        @return reference to the function object
        """
        return self._functionObject
    
    def lineno(self):
        """
        Public method returning the line number defining this object.
        
        return line number defining the object (integer)
        """
        return self._functionObject.lineno
    
    def lessThan(self, other, column, order):
        """
        Public method to check, if the item is less than the other one.
        
        @param other reference to item to compare against (BrowserItem)
        @param column column number to use for the comparison (integer)
        @param order sort order (Qt.SortOrder) (for special sorting)
        @return true, if this item is less than other (boolean)
        """
        if issubclass(other.__class__, BrowserMethodItem):
            if self.name.startswith('__init__'):
                return order == Qt.AscendingOrder
            if other.name.startswith('__init__'):
                return order == Qt.DescendingOrder
        elif issubclass(other.__class__, BrowserClassAttributesItem):
            return order == Qt.DescendingOrder
        
        if Preferences.getUI("BrowsersListContentsByOccurrence") and column == 0:
            if order == Qt.AscendingOrder:
                return self.lineno() < other.lineno()
            else:
                return self.lineno() > other.lineno()
        
        return BrowserItem.lessThan(self, other, column, order)
    
    def isPublic(self):
        """
        Public method returning the public visibility status.
        
        @return flag indicating public visibility (boolean)
        """
        return self._functionObject.isPublic()

class BrowserClassAttributesItem(BrowserItem):
    """
    Class implementing the data structure for browser class attributes items.
    """
    def __init__(self, parent, attributes, text):
        """
        Constructor
        
        @param parent parent item
        @param attributes list of attributes
        @param text text to be shown by this item (QString)
        """
        BrowserItem.__init__(self, parent, text)
        
        self.type_ = BrowserItemAttributes
        self._attributes = attributes.copy()
        self._populated = False
        self._lazyPopulation = True
        self.icon = UI.PixmapCache.getIcon("attributes.png")
    
    def attributes(self):
        """
        Public method returning the attribute list.
        
        @return reference to the list of attributes
        """
        return self._attributes
    
    def lessThan(self, other, column, order):
        """
        Public method to check, if the item is less than the other one.
        
        @param other reference to item to compare against (BrowserItem)
        @param column column number to use for the comparison (integer)
        @param order sort order (Qt.SortOrder) (for special sorting)
        @return true, if this item is less than other (boolean)
        """
        if issubclass(other.__class__, BrowserCodingItem):
            return order == Qt.DescendingOrder
        elif issubclass(other.__class__, BrowserClassItem) or \
             issubclass(other.__class__, BrowserMethodItem):
            return order == Qt.AscendingOrder
        
        return BrowserItem.lessThan(self, other, column, order)

class BrowserClassAttributeItem(BrowserItem):
    """
    Class implementing the data structure for browser class attribute items.
    """
    def __init__(self, parent, attribute):
        """
        Constructor
        
        @param parent parent item
        @param attribute reference to the attribute object
        """
        BrowserItem.__init__(self, parent, attribute.name)
        
        self.type_ = BrowserItemAttribute
        self._attributeObject = attribute
        self.__public = attribute.isPublic()
        if attribute.isPrivate():
            self.icon = UI.PixmapCache.getIcon("attribute_private.png")
        elif attribute.isProtected():
            self.icon = UI.PixmapCache.getIcon("attribute_protected.png")
        else:
            self.icon = UI.PixmapCache.getIcon("attribute.png")
    
    def isPublic(self):
        """
        Public method returning the public visibility status.
        
        @return flag indicating public visibility (boolean)
        """
        return self.__public
    
    def attributeObject(self):
        """
        Public method returning the class object.
        
        @return reference to the class object
        """
        return self._attributeObject
    
    def fileName(self):
        """
        Public method returning the filename.
        
        @return filename (string)
        """
        return self._attributeObject.file
    
    def lineno(self):
        """
        Public method returning the line number defining this object.
        
        return line number defining the object (integer)
        """
        return self._attributeObject.lineno
    
    def lessThan(self, other, column, order):
        """
        Public method to check, if the item is less than the other one.
        
        @param other reference to item to compare against (BrowserItem)
        @param column column number to use for the comparison (integer)
        @param order sort order (Qt.SortOrder) (for special sorting)
        @return true, if this item is less than other (boolean)
        """
        if Preferences.getUI("BrowsersListContentsByOccurrence") and column == 0:
            if order == Qt.AscendingOrder:
                return self.lineno() < other.lineno()
            else:
                return self.lineno() > other.lineno()
        
        return BrowserItem.lessThan(self, other, column, order)

class BrowserCodingItem(BrowserItem):
    """
    Class implementing the data structure for browser coding items.
    """
    def __init__(self, parent, text):
        """
        Constructor
        
        @param parent parent item
        @param text text to be shown by this item (QString)
        """
        BrowserItem.__init__(self, parent, text)
        
        self.type_ = BrowserItemCoding
        self.icon = UI.PixmapCache.getIcon("textencoding.png")
    
    def lessThan(self, other, column, order):
        """
        Public method to check, if the item is less than the other one.
        
        @param other reference to item to compare against (BrowserItem)
        @param column column number to use for the comparison (integer)
        @param order sort order (Qt.SortOrder) (for special sorting)
        @return true, if this item is less than other (boolean)
        """
        if issubclass(other.__class__, BrowserClassItem) or \
           issubclass(other.__class__, BrowserClassAttributesItem):
            return order == Qt.AscendingOrder
        
        return BrowserItem.lessThan(self, other, column, order)
