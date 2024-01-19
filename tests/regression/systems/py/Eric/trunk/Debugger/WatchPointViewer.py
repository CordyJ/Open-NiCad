# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the watch expression viewer widget.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox
from KdeQt.KQApplication import e4App

from EditWatchpointDialog import EditWatchpointDialog

import Utilities

class WatchPointViewer(QTreeView):
    """
    Class implementing the watch expression viewer widget.
    
    Watch expressions will be shown with all their details. They can be modified through
    the context menu of this widget.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent the parent (QWidget)
        """
        QTreeView.__init__(self,parent)
        self.setObjectName("WatchExpressionViewer")
        
        self.__model = None
        
        self.setItemsExpandable(False)
        self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.setWindowTitle(self.trUtf8("Watchpoints"))
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self,SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.__showContextMenu)
        self.connect(self,SIGNAL('doubleClicked(const QModelIndex &)'),
                     self.__doubleClicked)
        
        self.__createPopupMenus()
        
    def setModel(self, model):
        """
        Public slot to set the watch expression model.
        
        @param reference to the watch expression model (WatchPointModel)
        """
        self.__model = model
        
        self.sortingModel = QSortFilterProxyModel()
        self.sortingModel.setSourceModel(self.__model)
        QTreeView.setModel(self, self.sortingModel)
        
        header = self.header()
        header.setSortIndicator(0, Qt.AscendingOrder)
        header.setSortIndicatorShown(True)
        header.setClickable(True)
        
        self.setSortingEnabled(True)
        
        self.__layoutDisplay()
        
    def __layoutDisplay(self):
        """
        Private slot to perform a layout operation.
        """
        self.doItemsLayout()
        self.__resizeColumns()
        self.__resort()
        
    def __resizeColumns(self):
        """
        Private slot to resize the view when items get added, edited or deleted.
        """
        self.header().resizeSections(QHeaderView.ResizeToContents)
        self.header().setStretchLastSection(True)
    
    def __resort(self):
        """
        Private slot to resort the tree.
        """
        self.model().sort(self.header().sortIndicatorSection(), 
                          self.header().sortIndicatorOrder())
        
    def __toSourceIndex(self, index):
        """
        Private slot to convert an index to a source index.
        
        @param index index to be converted (QModelIndex)
        """
        return self.sortingModel.mapToSource(index)
        
    def __fromSourceIndex(self, sindex):
        """
        Private slot to convert a source index to an index.
        
        @param sindex source index to be converted (QModelIndex)
        """
        return self.sortingModel.mapFromSource(sindex)
        
    def __setRowSelected(self, index, selected = True):
        """
        Private slot to select a complete row.
        
        @param index index determining the row to be selected (QModelIndex)
        @param selected flag indicating the action (bool)
        """
        if not index.isValid():
            return
        
        if selected:
            flags = QItemSelectionModel.SelectionFlags(\
                QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        else:
            flags = QItemSelectionModel.SelectionFlags(\
                QItemSelectionModel.Deselect | QItemSelectionModel.Rows)
        self.selectionModel().select(index, flags)
        
    def __createPopupMenus(self):
        """
        Private method to generate the popup menus.
        """
        self.menu = QMenu()
        self.menu.addAction(self.trUtf8("Add"), self.__addWatchPoint)
        self.menu.addAction(self.trUtf8("Edit..."), self.__editWatchPoint)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8("Enable"), self.__enableWatchPoint)
        self.menu.addAction(self.trUtf8("Enable all"), self.__enableAllWatchPoints)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8("Disable"), self.__disableWatchPoint)
        self.menu.addAction(self.trUtf8("Disable all"), self.__disableAllWatchPoints)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8("Delete"), self.__deleteWatchPoint)
        self.menu.addAction(self.trUtf8("Delete all"), self.__deleteAllWatchPoints)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8("Configure..."), self.__configure)

        self.backMenuActions = {}
        self.backMenu = QMenu()
        self.backMenu.addAction(self.trUtf8("Add"), self.__addWatchPoint)
        self.backMenuActions["EnableAll"] = \
            self.backMenu.addAction(self.trUtf8("Enable all"), 
                self.__enableAllWatchPoints)
        self.backMenuActions["DisableAll"] = \
            self.backMenu.addAction(self.trUtf8("Disable all"), 
                self.__disableAllWatchPoints)
        self.backMenuActions["DeleteAll"] = \
            self.backMenu.addAction(self.trUtf8("Delete all"), 
                self.__deleteAllWatchPoints)
        self.backMenu.addSeparator()
        self.backMenu.addAction(self.trUtf8("Configure..."), self.__configure)
        self.connect(self.backMenu, SIGNAL('aboutToShow()'), self.__showBackMenu)

        self.multiMenu = QMenu()
        self.multiMenu.addAction(self.trUtf8("Add"), self.__addWatchPoint)
        self.multiMenu.addSeparator()
        self.multiMenu.addAction(self.trUtf8("Enable selected"), 
            self.__enableSelectedWatchPoints)
        self.multiMenu.addAction(self.trUtf8("Enable all"), self.__enableAllWatchPoints)
        self.multiMenu.addSeparator()
        self.multiMenu.addAction(self.trUtf8("Disable selected"), 
            self.__disableSelectedWatchPoints)
        self.multiMenu.addAction(self.trUtf8("Disable all"), self.__disableAllWatchPoints)
        self.multiMenu.addSeparator()
        self.multiMenu.addAction(self.trUtf8("Delete selected"), 
            self.__deleteSelectedWatchPoints)
        self.multiMenu.addAction(self.trUtf8("Delete all"), self.__deleteAllWatchPoints)
        self.multiMenu.addSeparator()
        self.multiMenu.addAction(self.trUtf8("Configure..."), self.__configure)
    
    def __showContextMenu(self, coord):
        """
        Private slot to show the context menu.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        cnt = self.__getSelectedItemsCount()
        if cnt <= 1:
            index = self.indexAt(coord)
            if index.isValid():
                cnt = 1
                self.__setRowSelected(index)
        coord = self.mapToGlobal(coord)
        if cnt > 1:
            self.multiMenu.popup(coord)
        elif cnt == 1:
            self.menu.popup(coord)
        else:
            self.backMenu.popup(coord)
    
    def __clearSelection(self):
        """
        Private slot to clear the selection.
        """
        for index in self.selectedIndexes():
            self.__setRowSelected(index, False)
            
    def __findDuplicates(self, cond, special, showMessage = False, index = QModelIndex()):
        """
        Private method to check, if an entry already exists.
        
        @param cond condition to check (string or QString)
        @param special special condition to check (string or QString)
        @param showMessage flag indicating a message should be shown,
            if a duplicate entry is found (boolean)
        @param index index that should not be considered duplicate (QModelIndex)
        @return flag indicating a duplicate entry (boolean)
        """
        cond = unicode(cond)
        special = unicode(special)
        idx = self.__model.getWatchPointIndex(cond, special)
        duplicate = idx.isValid() and idx.internalPointer() != index.internalPointer()
        if showMessage and duplicate:
            if not special:
                msg = self.trUtf8("""<p>A watch expression '<b>%1</b>'"""
                                  """ already exists.</p>""")\
                        .arg(Utilities.html_encode(unicode(cond)))
            else:
                msg = self.trUtf8("""<p>A watch expression '<b>%1</b>'"""
                                  """ for the variable <b>%2</b> already exists.</p>""")\
                        .arg(special)\
                        .arg(Utilities.html_encode(unicode(cond)))
            KQMessageBox.warning(None,
                self.trUtf8("Watch expression already exists"),
                msg)
        
        return duplicate
    
    def __clearSelection(self):
        """
        Private slot to clear the selection.
        """
        for index in self.selectedIndexes():
            self.__setRowSelected(index, False)
            
    def __addWatchPoint(self):
        """
        Private slot to handle the add watch expression context menu entry.
        """
        dlg = EditWatchpointDialog((QString(""), False, True, 0, QString("")), self)
        if dlg.exec_() == QDialog.Accepted:
            cond, temp, enabled, ignorecount, special = dlg.getData()
            if not self.__findDuplicates(cond, special, True):
                self.__model.addWatchPoint(cond, special, (temp, enabled, ignorecount))
                self.__resizeColumns()
                self.__resort()

    def __doubleClicked(self, index):
        """
        Private slot to handle the double clicked signal.
        
        @param index index of the entry that was double clicked (QModelIndex)
        """
        if index.isValid():
            self.__doEditWatchPoint(index)

    def __editWatchPoint(self):
        """
        Private slot to handle the edit watch expression context menu entry.
        """
        index = self.currentIndex()
        if index.isValid():
            self.__doEditWatchPoint(index)
    
    def __doEditWatchPoint(self, index):
        """
        Private slot to edit a watch expression.
        
        @param index index of watch expression to be edited (QModelIndex)
        """
        sindex = self.__toSourceIndex(index)
        if sindex.isValid():
            wp = self.__model.getWatchPointByIndex(sindex)
            if not wp:
                return
            
            cond, special, temp, enabled, count = wp[:5]
            
            dlg = EditWatchpointDialog(\
                (QString(cond), temp, enabled, count, QString(special)), self)
            if dlg.exec_() == QDialog.Accepted:
                cond, temp, enabled, count, special = dlg.getData()
                if not self.__findDuplicates(cond, special, True, index):
                    self.__model.setWatchPointByIndex(sindex, 
                        unicode(cond), unicode(special), (temp, enabled, count))
                    self.__resizeColumns()
                    self.__resort()

    def __setWpEnabled(self, index, enabled):
        """
        Private method to set the enabled status of a watch expression.
        
        @param index index of watch expression to be enabled/disabled (QModelIndex)
        @param enabled flag indicating the enabled status to be set (boolean)
        """
        sindex = self.__toSourceIndex(index)
        if sindex.isValid():
            self.__model.setWatchPointEnabledByIndex(sindex, enabled)
        
    def __enableWatchPoint(self):
        """
        Private slot to handle the enable watch expression context menu entry.
        """
        index = self.currentIndex()
        self.__setWpEnabled(index, True)
        self.__resizeColumns()
        self.__resort()

    def __enableAllWatchPoints(self):
        """
        Private slot to handle the enable all watch expressions context menu entry.
        """
        index = self.model().index(0, 0)
        while index.isValid():
            self.__setWpEnabled(index, True)
            index = self.indexBelow(index)
        self.__resizeColumns()
        self.__resort()

    def __enableSelectedWatchPoints(self):
        """
        Private slot to handle the enable selected watch expressions context menu entry.
        """
        for index in self.selectedIndexes():
            if index.column() == 0:
                self.__setWpEnabled(index, True)
        self.__resizeColumns()
        self.__resort()

    def __disableWatchPoint(self):
        """
        Private slot to handle the disable watch expression context menu entry.
        """
        index = self.currentIndex()
        self.__setWpEnabled(index, False)
        self.__resizeColumns()
        self.__resort()

    def __disableAllWatchPoints(self):
        """
        Private slot to handle the disable all watch expressions context menu entry.
        """
        index = self.model().index(0, 0)
        while index.isValid():
            self.__setWpEnabled(index, False)
            index = self.indexBelow(index)
        self.__resizeColumns()
        self.__resort()

    def __disableSelectedWatchPoints(self):
        """
        Private slot to handle the disable selected watch expressions context menu entry.
        """
        for index in self.selectedIndexes():
            if index.column() == 0:
                self.__setWpEnabled(index, False)
        self.__resizeColumns()
        self.__resort()

    def __deleteWatchPoint(self):
        """
        Private slot to handle the delete watch expression context menu entry.
        """
        index = self.currentIndex()
        sindex = self.__toSourceIndex(index)
        if sindex.isValid():
            self.__model.deleteWatchPointByIndex(sindex)
        
    def __deleteAllWatchPoints(self):
        """
        Private slot to handle the delete all watch expressions context menu entry.
        """
        self.__model.deleteAll()

    def __deleteSelectedWatchPoints(self):
        """
        Private slot to handle the delete selected watch expressions context menu entry.
        """
        idxList = []
        for index in self.selectedIndexes():
            sindex = self.__toSourceIndex(index)
            if sindex.isValid() and index.column() == 0:
                lastrow = index.row()
                idxList.append(sindex)
        self.__model.deleteWatchPoints(idxList)

    def __showBackMenu(self):
        """
        Private slot to handle the aboutToShow signal of the background menu.
        """
        if self.model().rowCount() == 0:
            self.backMenuActions["EnableAll"].setEnabled(False)
            self.backMenuActions["DisableAll"].setEnabled(False)
            self.backMenuActions["DeleteAll"].setEnabled(False)
        else:
            self.backMenuActions["EnableAll"].setEnabled(True)
            self.backMenuActions["DisableAll"].setEnabled(True)
            self.backMenuActions["DeleteAll"].setEnabled(True)

    def __getSelectedItemsCount(self):
        """
        Private method to get the count of items selected.
        
        @return count of items selected (integer)
        """
        count = len(self.selectedIndexes()) / (self.__model.columnCount()-1)
        # column count is 1 greater than selectable
        return count
    
    def __configure(self):
        """
        Private method to open the configuration dialog.
        """
        e4App().getObject("UserInterface").showPreferences("debuggerGeneralPage")
