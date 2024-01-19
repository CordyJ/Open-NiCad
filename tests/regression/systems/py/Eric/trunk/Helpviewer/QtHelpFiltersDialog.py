# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to manage the QtHelp filters.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtHelp import QHelpEngineCore

from KdeQt import KQInputDialog

from Ui_QtHelpFiltersDialog import Ui_QtHelpFiltersDialog

class QtHelpFiltersDialog(QDialog, Ui_QtHelpFiltersDialog):
    """
    Class implementing a dialog to manage the QtHelp filters
    """
    def __init__(self, engine, parent = None):
        """
        Constructor
        
        @param engine reference to the help engine (QHelpEngine)
        @param parent reference to the parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.__engine = engine
        
        self.attributesList.header().hide()
        
        self.filtersList.clear()
        self.attributesList.clear()
        
        help = QHelpEngineCore(self.__engine.collectionFile())
        help.setupData()
        
        self.__removedFilters = []
        self.__filterMap = {}
        self.__filterMapBackup = {}
        
        for filter in help.customFilters():
            atts = help.filterAttributes(filter)
            ufilter = unicode(filter)
            self.__filterMapBackup[ufilter] = atts
            if ufilter not in self.__filterMap:
                self.__filterMap[ufilter] = atts
        
        self.filtersList.addItems(sorted(self.__filterMap.keys()))
        for attr in help.filterAttributes():
            QTreeWidgetItem(self.attributesList, QStringList(attr))
        
        if self.__filterMap:
            self.filtersList.setCurrentRow(0)
    
    @pyqtSignature("QListWidgetItem*, QListWidgetItem*")
    def on_filtersList_currentItemChanged(self, current, previous):
        """
        Private slot to update the attributes depending on the current filter.
        
        @param current reference to the current item (QListWidgetitem)
        @param previous reference to the previous current item (QListWidgetItem)
        """
        checkedList = QStringList()
        if current is not None:
            checkedList = self.__filterMap[unicode(current.text())]
        for index in range(0, self.attributesList.topLevelItemCount()):
            itm = self.attributesList.topLevelItem(index)
            if checkedList.contains(itm.text(0)):
                itm.setCheckState(0, Qt.Checked)
            else:
                itm.setCheckState(0, Qt.Unchecked)
    
    @pyqtSignature("QTreeWidgetItem*, int")
    def on_attributesList_itemChanged(self, item, column):
        """
        Private slot to handle a change of an attribute.
        
        @param item reference to the changed item (QTreeWidgetItem)
        @param column column containing the change (integer)
        """
        if self.filtersList.currentItem() is None:
            return
        
        filter = unicode(self.filtersList.currentItem().text())
        if filter not in self.__filterMap:
            return
        
        newAtts = QStringList()
        for index in range(0, self.attributesList.topLevelItemCount()):
            itm = self.attributesList.topLevelItem(index)
            if itm.checkState(0) == Qt.Checked:
                newAtts.append(itm.text(0))
        self.__filterMap[filter] = newAtts
    
    @pyqtSignature("")
    def on_addButton_clicked(self):
        """
        Private slot to add a new filter.
        """
        filter, ok = KQInputDialog.getText(\
            None,
            self.trUtf8("Add Filter"),
            self.trUtf8("Filter name:"),
            QLineEdit.Normal)
        if filter.isEmpty():
            return
        
        ufilter = unicode(filter)
        if ufilter not in self.__filterMap:
            self.__filterMap[ufilter] = QStringList()
            self.filtersList.addItem(filter)
        
        itm = self.filtersList.findItems(filter, Qt.MatchCaseSensitive)[0]
        self.filtersList.setCurrentItem(itm)
    
    @pyqtSignature("")
    def on_removeButton_clicked(self):
        """
        Private slot to remove a filter.
        """
        itm = self.filtersList.takeItem(self.filtersList.currentRow())
        if itm is None:
            return
        
        del self.__filterMap[unicode(itm.text())]
        self.__removedFilters.append(itm.text())
        del itm
        if self.filtersList.count():
            self.filtersList.setCurrentRow(0)
    
    @pyqtSignature("")
    def on_buttonBox_accepted(self):
        """
        Private slot to update the database, if the dialog is accepted.
        """
        filtersChanged = False
        if len(self.__filterMapBackup) != len(self.__filterMap):
            filtersChanged = True
        else:
            for filter in self.__filterMapBackup:
                if filter not in self.__filterMap:
                    filtersChanged = True
                else:
                    oldFilterAtts = self.__filterMapBackup[filter]
                    newFilterAtts = self.__filterMap[filter]
                    if len(oldFilterAtts) != len(newFilterAtts):
                        filtersChanged = True
                    else:
                        for attr in oldFilterAtts:
                            if attr not in newFilterAtts:
                                filtersChanged = True
                                break
                
                if filtersChanged:
                    break
        
        if filtersChanged:
            for filter in self.__removedFilters:
                self.__engine.removeCustomFilter(filter)
            for filter in self.__filterMap:
                self.__engine.addCustomFilter(filter, self.__filterMap[filter])
            
            self.__engine.setupData()
        
        self.accept()
