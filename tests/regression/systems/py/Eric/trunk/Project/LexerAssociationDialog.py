# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter lexer associations for the project.
"""

import os

from pygments.lexers import get_all_lexers

from PyQt4.QtCore import Qt, QStringList, pyqtSignature, QString
from PyQt4.QtGui import QHeaderView, QTreeWidgetItem, QDialog

import QScintilla.Lexers

from Ui_LexerAssociationDialog import Ui_LexerAssociationDialog

class LexerAssociationDialog(QDialog, Ui_LexerAssociationDialog):
    """
    Class implementing a dialog to enter lexer associations for the project.
    """
    def __init__(self, project, parent = None):
        """
        Constructor
        
        @param project reference to the project object
        @param parent reference to the parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.editorLexerList.headerItem().setText(self.editorLexerList.columnCount(), "")
        header = self.editorLexerList.header()
        header.setResizeMode(QHeaderView.ResizeToContents)
        header.setSortIndicator(0, Qt.AscendingOrder)
        
        try:
            self.extsep = os.extsep
        except AttributeError:
            self.extsep = "."
        
        self.extras = ["-----------", self.trUtf8("Alternative")]
        languages = \
            [''] + sorted(QScintilla.Lexers.getSupportedLanguages().keys()) + self.extras
        for lang in languages:
            self.editorLexerCombo.addItem(lang)
        
        pygmentsLexers = [''] + sorted([l[0] for l in get_all_lexers()])
        for pygmentsLexer in pygmentsLexers:
            self.pygmentsLexerCombo.addItem(pygmentsLexer)
        
        # set initial values
        self.project = project
        for ext, lexer in self.project.pdata["LEXERASSOCS"].items():
            QTreeWidgetItem(self.editorLexerList, 
                QStringList() << ext << lexer)
        self.editorLexerList.sortByColumn(0, Qt.AscendingOrder)
    
    @pyqtSignature("")
    def on_addLexerButton_clicked(self):
        """
        Private slot to add the lexer association displayed to the list.
        """
        ext = self.editorFileExtEdit.text()
        if ext.startsWith(self.extsep):
            ext.replace(self.extsep, "")
        lexer = self.editorLexerCombo.currentText()
        if lexer in self.extras:
            pygmentsLexer = self.pygmentsLexerCombo.currentText()
            if pygmentsLexer.isEmpty():
                lexer = pygmentsLexer
            else:
                lexer = QString("Pygments|%1").arg(pygmentsLexer)
        if not ext.isEmpty() and not lexer.isEmpty():
            itmList = self.editorLexerList.findItems(\
                ext, Qt.MatchFlags(Qt.MatchExactly), 0)
            if itmList:
                index = self.editorLexerList.indexOfTopLevelItem(itmList[0])
                itm = self.editorLexerList.takeTopLevelItem(index)
                del itm
            itm = QTreeWidgetItem(self.editorLexerList, 
                QStringList() << ext << lexer)
            self.editorFileExtEdit.clear()
            self.editorLexerCombo.setCurrentIndex(0)
            self.pygmentsLexerCombo.setCurrentIndex(0)
            self.editorLexerList.sortItems(self.editorLexerList.sortColumn(), 
                self.editorLexerList.header().sortIndicatorOrder())
    
    @pyqtSignature("")
    def on_deleteLexerButton_clicked(self):
        """
        Private slot to delete the currently selected lexer association of the list.
        """
        itmList = self.editorLexerList.selectedItems()
        if itmList:
            index = self.editorLexerList.indexOfTopLevelItem(\
                        itmList[0])
            itm = self.editorLexerList.takeTopLevelItem(index)
            del itm
            
            self.editorLexerList.clearSelection()
            self.editorFileExtEdit.clear()
            self.editorLexerCombo.setCurrentIndex(0)
    
    def on_editorLexerList_itemClicked(self, itm, column):
        """
        Private slot to handle the clicked signal of the lexer association list.
        
        @param itm reference to the selecte item (QTreeWidgetItem)
        @param column column the item was clicked or activated (integer) (ignored)
        """
        if itm is None:
            self.editorFileExtEdit.clear()
            self.editorLexerCombo.setCurrentIndex(0)
            self.pygmentsLexerCombo.setCurrentIndex(0)
        else:
            self.editorFileExtEdit.setText(itm.text(0))
            lexer = itm.text(1)
            if lexer.startsWith("Pygments|"):
                pygmentsLexer = lexer.section("|", 1)
                pygmentsIndex = self.pygmentsLexerCombo.findText(pygmentsLexer)
                lexer = self.trUtf8("Alternative")
            else:
                pygmentsIndex = 0
            index = self.editorLexerCombo.findText(lexer)
            self.editorLexerCombo.setCurrentIndex(index)
            self.pygmentsLexerCombo.setCurrentIndex(pygmentsIndex)
    
    def on_editorLexerList_itemActivated(self, itm, column):
        """
        Private slot to handle the activated signal of the lexer association list.
        
        @param itm reference to the selecte item (QTreeWidgetItem)
        @param column column the item was clicked or activated (integer) (ignored)
        """
        self.on_editorLexerList_itemClicked(itm, column)
    
    @pyqtSignature("QString")
    def on_editorLexerCombo_currentIndexChanged(self, text):
        """
        Private slot to handle the selection of a lexer.
        """
        if text in self.extras:
            self.pygmentsLexerCombo.setEnabled(True)
            self.pygmentsLabel.setEnabled(True)
        else:
            self.pygmentsLexerCombo.setEnabled(False)
            self.pygmentsLabel.setEnabled(False)

    def transferData(self):
        """
        Public slot to transfer the associations into the projects data structure.
        """
        self.project.pdata["LEXERASSOCS"] = {}
        for index in range(self.editorLexerList.topLevelItemCount()):
            itm = self.editorLexerList.topLevelItem(index)
            pattern = unicode(itm.text(0))
            self.project.pdata["LEXERASSOCS"][pattern] = unicode(itm.text(1))
