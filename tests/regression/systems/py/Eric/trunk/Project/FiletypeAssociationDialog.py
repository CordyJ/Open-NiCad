# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter filetype associations for the project.
"""

import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_FiletypeAssociationDialog import Ui_FiletypeAssociationDialog

class FiletypeAssociationDialog(QDialog, Ui_FiletypeAssociationDialog):
    """
    Class implementing a dialog to enter filetype associations for the project.
    """
    def __init__(self, project, parent = None):
        """
        Constructor
        
        @param project reference to the project object
        @param parent reference to the parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.filetypeAssociationList.headerItem().setText(
            self.filetypeAssociationList.columnCount(), "")
        self.filetypeAssociationList.header().setSortIndicator(0, Qt.AscendingOrder)
        
        # keep these lists in sync
        self.filetypes = ["SOURCES", "FORMS", "TRANSLATIONS", "RESOURCES", "INTERFACES", 
                          "OTHERS", "__IGNORE__"]
        self.filetypeStrings = [self.trUtf8("Sources"), self.trUtf8("Forms"),
                                self.trUtf8("Translations"), self.trUtf8("Resources"),
                                self.trUtf8("Interfaces"), self.trUtf8("Others"), 
                                self.trUtf8("Ignore")]
        self.filetypesList = QStringList()
        for fts in self.filetypeStrings:
            self.filetypesList.append(fts)
        self.filetypeCombo.addItems(self.filetypesList)
        
        self.project = project
        for pattern, filetype in self.project.pdata["FILETYPES"].items():
            try:
                index = self.filetypes.index(filetype)
                itm = self.__createItem(pattern, self.filetypeStrings[index])
            except ValueError:
                pass    # silently discard entries of unknown type
        
        self.__resort()
        self.__reformat()
        
    def __resort(self):
        """
        Private method to resort the tree.
        """
        self.filetypeAssociationList.sortItems(self.filetypeAssociationList.sortColumn(), 
            self.filetypeAssociationList.header().sortIndicatorOrder())
        
    def __reformat(self):
        """
        Private method to reformat the tree.
        """
        self.filetypeAssociationList.header().resizeSections(QHeaderView.ResizeToContents)
        self.filetypeAssociationList.header().setStretchLastSection(True)
        
    def __createItem(self, pattern, filetype):
        """
        Private slot to create a new entry in the association list.
        
        @param pattern pattern of the entry (string or QString)
        @param filetype file type of the entry (string or QString)
        @return reference to the newly generated entry (QTreeWidgetItem)
        """
        itm = QTreeWidgetItem(self.filetypeAssociationList,
            QStringList() << pattern << filetype)
        return itm
        
    def on_filetypeAssociationList_currentItemChanged(self, itm, prevItm):
        """
        Private slot to handle the currentItemChanged signal of the association list.
        
        @param itm reference to the new current item (QTreeWidgetItem)
        @param prevItm reference to the previous current item (QTreeWidgetItem)
        """
        if itm is None:
            self.filePatternEdit.clear()
            self.filetypeCombo.setCurrentIndex(0)
            self.deleteAssociationButton.setEnabled(False)
        else:
            self.filePatternEdit.setText(itm.text(0))
            self.filetypeCombo.setCurrentIndex(self.filetypeCombo.findText(itm.text(1)))
            self.deleteAssociationButton.setEnabled(True)

    @pyqtSignature("")
    def on_addAssociationButton_clicked(self):
        """
        Private slot to add the association displayed to the list.
        """
        pattern = self.filePatternEdit.text()
        filetype = self.filetypeCombo.currentText()
        if not pattern.isEmpty():
            items = self.filetypeAssociationList.findItems(\
                pattern, Qt.MatchFlags(Qt.MatchExactly), 0)
            for itm in items:
                itm = self.filetypeAssociationList.takeTopLevelItem(\
                    self.filetypeAssociationList.indexOfTopLevelItem(itm))
                del itm
            itm = self.__createItem(pattern, filetype)
            self.__resort()
            self.__reformat()
            self.filePatternEdit.clear()
            self.filetypeCombo.setCurrentIndex(0)
            self.filetypeAssociationList.setCurrentItem(itm)

    @pyqtSignature("")
    def on_deleteAssociationButton_clicked(self):
        """
        Private slot to delete the currently selected association of the listbox.
        """
        for itm in self.filetypeAssociationList.selectedItems():
            itm = self.filetypeAssociationList.takeTopLevelItem(\
                self.filetypeAssociationList.indexOfTopLevelItem(itm))
            del itm
            
            self.filetypeAssociationList.clearSelection()
            self.filePatternEdit.clear()
            self.filetypeCombo.setCurrentIndex(0)

    def on_filePatternEdit_textChanged(self, txt):
        """
        Private slot to handle the textChanged signal of the pattern lineedit.
        
        @param txt text of the lineedit (QString)
        """
        if txt.isEmpty():
            self.addAssociationButton.setEnabled(False)
            self.deleteAssociationButton.setEnabled(False)
        else:
            self.addAssociationButton.setEnabled(True)
            if len(self.filetypeAssociationList.selectedItems()) == 0:
                self.deleteAssociationButton.setEnabled(False)
            else:
                self.deleteAssociationButton.setEnabled(\
                    self.filetypeAssociationList.selectedItems()[0].text(0) == txt)

    def transferData(self):
        """
        Public slot to transfer the associations into the projects data structure.
        """
        self.project.pdata["FILETYPES"] = {}
        for index in range(self.filetypeAssociationList.topLevelItemCount()):
            itm = self.filetypeAssociationList.topLevelItem(index)
            pattern = unicode(itm.text(0))
            index = self.filetypeStrings.index(itm.text(1))
            self.project.pdata["FILETYPES"][pattern] = self.filetypes[index]
