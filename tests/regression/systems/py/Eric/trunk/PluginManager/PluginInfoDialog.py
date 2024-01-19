# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing the Plugin Info Dialog.
"""

from PyQt4.QtCore import QStringList, Qt,  SIGNAL
from PyQt4.QtGui import QDialog, QTreeWidgetItem, QHeaderView, QMenu, QBrush
from PyQt4.QtCore import pyqtSignature

from PluginDetailsDialog import PluginDetailsDialog

from Ui_PluginInfoDialog import Ui_PluginInfoDialog

class PluginInfoDialog(QDialog, Ui_PluginInfoDialog):
    """
    Class implementing the Plugin Info Dialog.
    """
    def __init__(self, pluginManager, parent = None):
        """
        Constructor
        
        @param pluginManager reference to the plugin manager object
        @param parent parent of this dialog (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.pm = pluginManager
        
        self.__autoActivateColumn = 3
        self.__activeColumn = 4
        
        self.pluginList.headerItem().setText(self.pluginList.columnCount(), "")
        
        # populate the list
        self.__populateList()
        self.pluginList.sortByColumn(0, Qt.AscendingOrder)
        
        self.__menu = QMenu(self)
        self.__menu.addAction(self.trUtf8('Show details'), self.__showDetails)
        self.__activateAct = \
            self.__menu.addAction(self.trUtf8('Activate'), self.__activatePlugin)
        self.__deactivateAct = \
            self.__menu.addAction(self.trUtf8('Deactivate'), self.__deactivatePlugin)
        self.pluginList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.pluginList, 
                     SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.__showContextMenu)
    
    def __populateList(self):
        """
        Private method to (re)populate the list of plugins.
        """
        self.pluginList.clear()
        for info in self.pm.getPluginInfos():
            self.__createEntry(info)
        self.pluginList.sortItems(self.pluginList.sortColumn(), 
                                  self.pluginList.header().sortIndicatorOrder())
        
    def __createEntry(self, info):
        """
        Private method to create a list entry based on the provided info.
        
        @param info tuple giving the info for the entry
        """
        infoList = QStringList() \
            << info[0] \
            << info[1] \
            << info[2] \
            << (info[3] and self.trUtf8("Yes") or self.trUtf8("No")) \
            << (info[4] and self.trUtf8("Yes") or self.trUtf8("No")) \
            << info[5]
        itm = QTreeWidgetItem(self.pluginList, infoList)
        if info[6]:
            # plugin error
            for col in range(self.pluginList.columnCount()):
                itm.setForeground(col, QBrush(Qt.red))
        itm.setTextAlignment(self.__autoActivateColumn, Qt.AlignHCenter)
        itm.setTextAlignment(self.__activeColumn, Qt.AlignHCenter)
        
        self.pluginList.header().resizeSections(QHeaderView.ResizeToContents)
        self.pluginList.header().setStretchLastSection(True)
    
    def __showContextMenu(self, coord):
        """
        Private slot to show the context menu of the listview.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        itm = self.pluginList.itemAt(coord)
        if itm is not None:
            autoactivate = itm.text(self.__autoActivateColumn) == self.trUtf8("Yes")
            if itm.text(self.__activeColumn) == self.trUtf8("Yes"):
                self.__activateAct.setEnabled(False)
                self.__deactivateAct.setEnabled(autoactivate)
            else:
                self.__activateAct.setEnabled(autoactivate)
                self.__deactivateAct.setEnabled(False)
            self.__menu.popup(self.mapToGlobal(coord))
    
    @pyqtSignature("QTreeWidgetItem*, int")
    def on_pluginList_itemActivated(self, item, column):
        """
        Private slot to show details about a plugin.
        
        @param item reference to the selected item (QTreeWidgetItem)
        @param column column number (integer)
        """
        moduleName = unicode(item.text(0))
        details = self.pm.getPluginDetails(moduleName)
        if details is None:
            pass
        else:
            dlg = PluginDetailsDialog(details, self)
            dlg.show()
    
    def __showDetails(self):
        """
        Private slot to handle the "Show details" context menu action.
        """
        itm = self.pluginList.currentItem()
        self.on_pluginList_itemActivated(itm, 0)
    
    def __activatePlugin(self):
        """
        Private slot to handle the "Deactivate" context menu action.
        """
        itm = self.pluginList.currentItem()
        moduleName = unicode(itm.text(0))
        self.pm.activatePlugin(moduleName)
        # repopulate the list
        self.__populateList()
    
    def __deactivatePlugin(self):
        """
        Private slot to handle the "Activate" context menu action.
        """
        itm = self.pluginList.currentItem()
        moduleName = unicode(itm.text(0))
        self.pm.deactivatePlugin(moduleName)
        # repopulate the list
        self.__populateList()
