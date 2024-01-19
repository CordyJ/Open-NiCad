# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to manage the QtHelp documentation database.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtHelp import QHelpEngineCore

from KdeQt import KQFileDialog, KQMessageBox

from Ui_QtHelpDocumentationDialog import Ui_QtHelpDocumentationDialog

class QtHelpDocumentationDialog(QDialog, Ui_QtHelpDocumentationDialog):
    """
    Class implementing a dialog to manage the QtHelp documentation database.
    """
    def __init__(self, engine, parent):
        """
        Constructor
        
        @param engine reference to the help engine (QHelpEngine)
        @param parent reference to the parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.removeButton.setEnabled(False)
        
        self.__engine = engine
        self.__mw = parent
        
        docs = self.__engine.registeredDocumentations()
        self.documentsList.addItems(docs)
        
        self.__registeredDocs = []
        self.__unregisteredDocs = []
        self.__tabsToClose = []
    
    @pyqtSignature("")
    def on_documentsList_itemSelectionChanged(self):
        """
        Private slot handling a change of the documents selection.
        """
        self.removeButton.setEnabled(len(self.documentsList.selectedItems()) != 0)
    
    @pyqtSignature("")
    def on_addButton_clicked(self):
        """
        Private slot to add documents to the help database.
        """
        fileNames = KQFileDialog.getOpenFileNames(\
            self,
            self.trUtf8("Add Documentation"),
            QString(),
            self.trUtf8("Qt Compressed Help Files (*.qch)"),
            None)
        if fileNames.isEmpty():
            return
        
        for fileName in fileNames:
            ns = QHelpEngineCore.namespaceName(fileName)
            if ns.isEmpty():
                KQMessageBox.warning(self,
                    self.trUtf8("Add Documentation"),
                    self.trUtf8("""The file <b>%1</b> is not a valid Qt Help File.""")\
                        .arg(fileName)
                )
                continue
            
            if len(self.documentsList.findItems(ns, Qt.MatchFixedString)):
                KQMessageBox.warning(self,
                    self.trUtf8("Add Documentation"),
                    self.trUtf8("""The namespace <b>%1</b> is already registered.""")\
                        .arg(ns)
                )
                continue
            
            self.__engine.registerDocumentation(fileName)
            self.documentsList.addItem(ns)
            self.__registeredDocs.append(ns)
            if ns in self.__unregisteredDocs:
                self.__unregisteredDocs.remove(ns)

    @pyqtSignature("")
    def on_removeButton_clicked(self):
        """
        Private slot to remove a document from the help database.
        """
        res = KQMessageBox.question(None,
            self.trUtf8("Remove Documentation"),
            self.trUtf8("""Do you really want to remove the selected documentation """
                        """sets from the database?"""),
            QMessageBox.StandardButtons(\
                QMessageBox.No | \
                QMessageBox.Yes),
            QMessageBox.No)
        if res == QMessageBox.No:
            return
        
        openedDocs = self.__mw.getSourceFileList()
        
        items = self.documentsList.selectedItems()
        for item in items:
            ns = item.text()
            if ns in openedDocs.values():
                res = KQMessageBox.information(self,
                    self.trUtf8("Remove Documentation"),
                    self.trUtf8("""Some documents currently opened reference the """
                                """documentation you are attempting to remove. """
                                """Removing the documentation will close those """
                                """documents."""),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Cancel | \
                        QMessageBox.Ok))
                if res == QMessageBox.Cancel:
                    return
            self.__unregisteredDocs.append(ns)
            for id in openedDocs:
                if openedDocs[id] == ns and id not in self.__tabsToClose:
                    self.__tabsToClose.append(id)
            itm = self.documentsList.takeItem(self.documentsList.row(item))
            del itm
            
            self.__engine.unregisterDocumentation(ns)
        
        if self.documentsList.count():
            self.documentsList.setCurrentRow(0, QItemSelectionModel.ClearAndSelect)
    
    def hasChanges(self):
        """
        Public slot to test the dialog for changes.
        
        @return flag indicating presence of changes
        """
        return len(self.__registeredDocs) > 0 or \
               len(self.__unregisteredDocs) > 0
    
    def getTabsToClose(self):
        """
        Public method to get the list of tabs to close.
        
        @return list of tab ids to be closed (list of integers)
        """
        return self.__tabsToClose
