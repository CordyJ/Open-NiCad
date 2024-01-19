# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the spell checking dialog.
"""

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import *

from Ui_SpellCheckingDialog import Ui_SpellCheckingDialog

import Utilities

class SpellCheckingDialog(QDialog, Ui_SpellCheckingDialog):
    """
    Class implementing the spell checking dialog.
    """
    def __init__(self, spellChecker, startPos, endPos, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.__spell = spellChecker
        self.languageLabel.setText("<b>%s</b>" % self.__spell.getLanguage())
        if not self.__spell.initCheck(startPos, endPos):
            self.__enableButtons(False)
        else:
            self.__advance()
    
    def __enableButtons(self, enable):
        """
        Private method to set the buttons enabled state.
        """
        self.addButton.setEnabled(enable)
        self.ignoreButton.setEnabled(enable)
        self.ignoreAllButton.setEnabled(enable)
        self.replaceButton.setEnabled(enable)
        self.replaceAllButton.setEnabled(enable)
    
    def __advance(self):
        """
        Private method to advance to the next error.
        """
        try:
            self.__spell.next()
        except StopIteration:
            self.__enableButtons(False)
            self.contextLabel.setText("")
            self.changeEdit.setText("")
            self.suggestionsList.clear()
            return
        
        self.__enableButtons(True)
        self.word, self.wordStart, self.wordEnd = self.__spell.getError()
        lcontext, rcontext = self.__spell.getContext(self.wordStart, self.wordEnd)
        self.changeEdit.setText(self.word)
        self.contextLabel.setText(QString('%1<font color="#FF0000">%2</font>%3')\
                                  .arg(Utilities.html_encode(unicode(lcontext)))\
                                  .arg(self.word)\
                                  .arg(Utilities.html_encode(unicode(rcontext))))
        suggestions = self.__spell.getSuggestions(self.word)
        self.suggestionsList.clear()
        self.suggestionsList.addItems(suggestions)
    
    @pyqtSignature("QString")
    def on_changeEdit_textChanged(self, text):
        """
        Private method to handle a change of the replacement text.
        
        @param text contents of the line edit (QString)
        """
        self.replaceButton.setEnabled(not text.isEmpty())
        self.replaceAllButton.setEnabled(not text.isEmpty())
    
    @pyqtSignature("QString")
    def on_suggestionsList_currentTextChanged(self, currentText):
        """
        Private method to handle the selection of a suggestion.
        
        @param currentText the currently selected text (QString)
        """
        if not currentText.isEmpty():
            self.changeEdit.setText(currentText)
    
    @pyqtSignature("")
    def on_ignoreButton_clicked(self):
        """
        Private slot to ignore the found error.
        """
        self.__advance()
    
    @pyqtSignature("")
    def on_ignoreAllButton_clicked(self):
        """
        Private slot to always ignore the found error.
        """
        self.__spell.ignoreAlways()
        self.__advance()
    
    @pyqtSignature("")
    def on_addButton_clicked(self):
        """
        Private slot to add the current word to the personal word list.
        """
        self.__spell.add()
        self.__advance()
    
    @pyqtSignature("")
    def on_replaceButton_clicked(self):
        """
        Private slot to replace the current word with the given replacement.
        """
        self.__spell.replace(self.changeEdit.text())
        self.__advance()
    
    @pyqtSignature("")
    def on_replaceAllButton_clicked(self):
        """
        Private slot to replace the current word with the given replacement.
        """
        self.__spell.replaceAlways(self.changeEdit.text())
        self.__advance()
