# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a configuration dialog for the tools menu.
"""

import sys
import os
import copy

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQMessageBox

from Ui_ToolGroupConfigurationDialog import Ui_ToolGroupConfigurationDialog
import Utilities

class ToolGroupConfigurationDialog(QDialog, Ui_ToolGroupConfigurationDialog):
    """
    Class implementing a configuration dialog for the tool groups.
    """
    def __init__(self, toolGroups, currentGroup, parent = None):
        """
        Constructor
        
        @param toolGroups list of configured tool groups
        @param currentGroup number of the active group (integer)
        @param parent parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.currentGroup = currentGroup
        self.toolGroups = copy.deepcopy(toolGroups)
        for group in toolGroups:
            self.groupsList.addItem(group[0])
        
        if len(toolGroups):
            self.groupsList.setCurrentRow(0)
            self.on_groupsList_currentRowChanged(0)
        
    @pyqtSignature("")
    def on_newButton_clicked(self):
        """
        Private slot to clear all entry fields.
        """
        self.nameEdit.clear()
        
    @pyqtSignature("")
    def on_addButton_clicked(self):
        """
        Private slot to add a new entry.
        """
        groupName = self.nameEdit.text()
        
        if groupName.isEmpty():
            KQMessageBox.critical(self,
                self.trUtf8("Add tool group entry"),
                self.trUtf8("You have to give a name for the group to add."))
            return
        
        if len(self.groupsList.findItems(groupName, Qt.MatchFlags(Qt.MatchExactly))):
            KQMessageBox.critical(self,
                self.trUtf8("Add tool group entry"),
                self.trUtf8("An entry for the group name %1 already exists.")\
                    .arg(groupName))
            return
        
        self.groupsList.addItem(unicode(groupName))
        self.toolGroups.append([unicode(groupName), []])
    
    @pyqtSignature("")
    def on_changeButton_clicked(self):
        """
        Private slot to change an entry.
        """
        row = self.groupsList.currentRow()
        if row < 0:
            return
        
        groupName = self.nameEdit.text()
        
        if groupName.isEmpty():
            KQMessageBox.critical(self,
                self.trUtf8("Add tool group entry"),
                self.trUtf8("You have to give a name for the group to add."))
            return
        
        if len(self.groupsList.findItems(groupName, Qt.MatchFlags(Qt.MatchExactly))):
            KQMessageBox.critical(self,
                self.trUtf8("Add tool group entry"),
                self.trUtf8("An entry for the group name %1 already exists.")\
                    .arg(groupName))
            return
            
        self.toolGroups[row][0] = unicode(groupName)
        self.groupsList.currentItem().setText(groupName)
        
    @pyqtSignature("")
    def on_deleteButton_clicked(self):
        """
        Private slot to delete the selected entry.
        """
        row = self.groupsList.currentRow()
        if row < 0:
            return
        
        res = KQMessageBox.warning(None,
            self.trUtf8("Delete tool group entry"),
            self.trUtf8("""<p>Do you really want to delete the tool group"""
                        """ <b>"%1"</b>?</p>""")\
                .arg(self.groupsList.currentItem().text()),
            QMessageBox.StandardButtons(\
                QMessageBox.No | \
                QMessageBox.Yes),
            QMessageBox.No)
        if res != QMessageBox.Yes:
            return
        
        if row == self.currentGroup:
            # set to default group if current group gets deleted
            self.currentGroup = -1
        
        del self.toolGroups[row]
        itm = self.groupsList.takeItem(row)
        del itm
        if row >= len(self.toolGroups):
            row -= 1
        self.groupsList.setCurrentRow(row)
        self.on_groupsList_currentRowChanged(row)
        
    @pyqtSignature("")
    def on_downButton_clicked(self):
        """
        Private slot to move an entry down in the list.
        """
        curr = self.groupsList.currentRow()
        self.__swap(curr, curr+1)
        self.groupsList.clear()
        for group in self.toolGroups:
            self.groupsList.addItem(group[0])
        self.groupsList.setCurrentRow(curr + 1)
        if curr + 1 == len(self.toolGroups):
            self.downButton.setEnabled(False)
        self.upButton.setEnabled(True)
        
    @pyqtSignature("")
    def on_upButton_clicked(self):
        """
        Private slot to move an entry up in the list.
        """
        curr = self.groupsList.currentRow()
        self.__swap(curr-1, curr)
        self.groupsList.clear()
        for group in self.toolGroups:
            self.groupsList.addItem(group[0])
        self.groupsList.setCurrentRow(curr - 1)
        if curr - 1 == 0:
            self.upButton.setEnabled(False)
        self.downButton.setEnabled(True)
        
    def on_groupsList_currentRowChanged(self, row):
        """
        Private slot to set the lineedits depending on the selected entry.
        
        @param row the row of the selected entry (integer)
        """
        if row >= 0 and row < len(self.toolGroups):
            group = self.toolGroups[row]
            self.nameEdit.setText(group[0])
            
            self.deleteButton.setEnabled(True)
            self.changeButton.setEnabled(True)
            
            if row != 0:
                self.upButton.setEnabled(True)
            else:
                self.upButton.setEnabled(False)
            
            if row+1 != len(self.toolGroups):
                self.downButton.setEnabled(True)
            else:
                self.downButton.setEnabled(False)
        else:
            self.nameEdit.clear()
            self.downButton.setEnabled(False)
            self.upButton.setEnabled(False)
            self.deleteButton.setEnabled(False)
            self.changeButton.setEnabled(False)
        
    def getToolGroups(self):
        """
        Public method to retrieve the tool groups. 
        
        @return a list of lists containing the group name and the
            tool group entries
        """
        return self.toolGroups[:], self.currentGroup
        
    def __swap(self, itm1, itm2):
        """
        Private method used two swap two list entries given by their index.
        
        @param itm1 index of first entry (int)
        @param itm2 index of second entry (int)
        """
        tmp = self.toolGroups[itm1]
        self.toolGroups[itm1] = self.toolGroups[itm2]
        self.toolGroups[itm2] = tmp
