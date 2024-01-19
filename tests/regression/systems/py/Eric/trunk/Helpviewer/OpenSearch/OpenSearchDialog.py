# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog for the configuration of search engines.
"""

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature, QString, SIGNAL

from KdeQt import KQFileDialog, KQMessageBox

from E4Gui.E4ListView import E4ListView

from Helpviewer.HelpWebSearchWidget import HelpWebSearchWidget

from OpenSearchEngineModel import OpenSearchEngineModel
from OpenSearchEditDialog import OpenSearchEditDialog

from Ui_OpenSearchDialog import Ui_OpenSearchDialog

class OpenSearchDialog(QDialog, Ui_OpenSearchDialog):
    """
    Class implementing a dialog for the configuration of search engines.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.setModal(True)
        
        self.__model = \
            OpenSearchEngineModel(HelpWebSearchWidget.openSearchManager(), self)
        self.enginesTable.setModel(self.__model)
        self.enginesTable.horizontalHeader().resizeSection(0, 200)
        self.enginesTable.horizontalHeader().setStretchLastSection(True)
        self.enginesTable.verticalHeader().hide()
        self.enginesTable.verticalHeader().setDefaultSectionSize(
            1.2 * self.fontMetrics().height())
        
        self.connect(self.enginesTable.selectionModel(), 
                     SIGNAL("selectionChanged(const QItemSelection&, const QItemSelection&)"), 
                     self.__selectionChanged)
        self.editButton.setEnabled(False)
    
    @pyqtSignature("")
    def on_addButton_clicked(self):
        """
        Private slot to add a new search engine.
        """
        fileNames = KQFileDialog.getOpenFileNames(\
            self,
            self.trUtf8("Add search engine"),
            QString(),
            self.trUtf8("OpenSearch (*.xml);;All Files (*)"),
            None)
        
        osm = HelpWebSearchWidget.openSearchManager()
        for fileName in fileNames:
            if not osm.addEngine(fileName):
                KQMessageBox.critical(self,
                    self.trUtf8("Add search engine"),
                    self.trUtf8("""%1 is not a valid OpenSearch 1.1 description or"""
                                """ is already on your list.""").arg(fileName))
    
    @pyqtSignature("")
    def on_deleteButton_clicked(self):
        """
        Private slot to delete the selected search engines.
        """
        if self.enginesTable.model().rowCount() == 1:
            KQMessageBox.critical(self,
                self.trUtf8("Delete selected engines"),
                self.trUtf8("""You must have at least one search engine."""))
        
        self.enginesTable.removeSelected()
    
    @pyqtSignature("")
    def on_restoreButton_clicked(self):
        """
        Private slot to restore the default search engines.
        """
        HelpWebSearchWidget.openSearchManager().restoreDefaults()
    
    @pyqtSignature("")
    def on_editButton_clicked(self):
        """
        Private slot to edit the data of the current search engine.
        """
        rows = self.enginesTable.selectionModel().selectedRows()
        if len(rows) == 0:
            row = self.enginesTable.selectionModel().currentIndex().row()
        else:
            row = rows[0].row()
        
        osm = HelpWebSearchWidget.openSearchManager()
        engineName = osm.allEnginesNames()[row]
        engine = osm.engine(engineName)
        dlg = OpenSearchEditDialog(engine, self)
        if dlg.exec_() == QDialog.Accepted:
            osm.enginesChanged()
    
    def __selectionChanged(self, selected, deselected):
        """
        Private slot to handle a change of the selection.
        
        @param selected item selection of selected items (QItemSelection)
        @param deselected item selection of deselected items (QItemSelection)
        """
        self.editButton.setEnabled(
            len(self.enginesTable.selectionModel().selectedRows()) <= 1)
