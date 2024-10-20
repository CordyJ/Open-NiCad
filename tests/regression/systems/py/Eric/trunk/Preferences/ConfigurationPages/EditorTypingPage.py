# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor Typing configuration page.
"""

from PyQt4.QtCore import QVariant, pyqtSignature

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorTypingPage import Ui_EditorTypingPage

import Preferences

class EditorTypingPage(ConfigurationPageBase, Ui_EditorTypingPage):
    """
    Class implementing the Editor Typing configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorTypingPage")
        
        # set initial values
        self.pageIds = {}
        self.pageIds[' '] = self.stackedWidget.indexOf(self.emptyPage)
        self.pageIds['Python'] = self.stackedWidget.indexOf(self.pythonPage)
        self.pageIds['Ruby'] = self.stackedWidget.indexOf(self.rubyPage)
        languages = self.pageIds.keys()
        languages.sort()
        for language in languages:
            self.languageCombo.addItem(language, QVariant(self.pageIds[language]))
        
        # Python
        self.pythonGroup.setChecked(\
            Preferences.getEditorTyping("Python/EnabledTypingAids"))
        self.pythonInsertClosingBraceCheckBox.setChecked(\
            Preferences.getEditorTyping("Python/InsertClosingBrace"))
        self.pythonSkipBraceCheckBox.setChecked(\
            Preferences.getEditorTyping("Python/SkipBrace"))
        self.pythonIndentBraceCheckBox.setChecked(\
            Preferences.getEditorTyping("Python/IndentBrace"))
        self.pythonInsertQuoteCheckBox.setChecked(\
            Preferences.getEditorTyping("Python/InsertQuote"))
        self.pythonDedentElseCheckBox.setChecked(\
            Preferences.getEditorTyping("Python/DedentElse"))
        self.pythonDedentExceptCheckBox.setChecked(\
            Preferences.getEditorTyping("Python/DedentExcept"))
        self.pythonDedentExceptPy24CheckBox.setChecked(\
            Preferences.getEditorTyping("Python/Py24StyleTry"))
        self.pythonInsertImportCheckBox.setChecked(\
            Preferences.getEditorTyping("Python/InsertImport"))
        self.pythonInsertSelfCheckBox.setChecked(\
            Preferences.getEditorTyping("Python/InsertSelf"))
        self.pythonInsertBlankCheckBox.setChecked(\
            Preferences.getEditorTyping("Python/InsertBlank"))
        self.pythonColonDetectionCheckBox.setChecked(\
            Preferences.getEditorTyping("Python/ColonDetection"))
        self.pythonDedentDefCheckBox.setChecked(
            Preferences.getEditorTyping("Python/DedentDef"))
        
        # Ruby
        self.rubyGroup.setChecked(\
            Preferences.getEditorTyping("Ruby/EnabledTypingAids"))
        self.rubyInsertClosingBraceCheckBox.setChecked(\
            Preferences.getEditorTyping("Ruby/InsertClosingBrace"))
        self.rubySkipBraceCheckBox.setChecked(\
            Preferences.getEditorTyping("Ruby/SkipBrace"))
        self.rubyIndentBraceCheckBox.setChecked(\
            Preferences.getEditorTyping("Ruby/IndentBrace"))
        self.rubyInsertQuoteCheckBox.setChecked(\
            Preferences.getEditorTyping("Ruby/InsertQuote"))
        self.rubyInsertBlankCheckBox.setChecked(\
            Preferences.getEditorTyping("Ruby/InsertBlank"))
        self.rubyInsertHereDocCheckBox.setChecked(\
            Preferences.getEditorTyping("Ruby/InsertHereDoc"))
        self.rubyInsertInlineDocCheckBox.setChecked(\
            Preferences.getEditorTyping("Ruby/InsertInlineDoc"))
        
        self.on_languageCombo_activated(' ')
        
    def save(self):
        """
        Public slot to save the Editor Typing configuration.
        """
        # Python
        Preferences.setEditorTyping("Python/EnabledTypingAids",
            int(self.pythonGroup.isChecked()))
        Preferences.setEditorTyping("Python/InsertClosingBrace",
            int(self.pythonInsertClosingBraceCheckBox.isChecked()))
        Preferences.setEditorTyping("Python/SkipBrace",
            int(self.pythonSkipBraceCheckBox.isChecked()))
        Preferences.setEditorTyping("Python/IndentBrace",
            int(self.pythonIndentBraceCheckBox.isChecked()))
        Preferences.setEditorTyping("Python/InsertQuote",
            int(self.pythonInsertQuoteCheckBox.isChecked()))
        Preferences.setEditorTyping("Python/DedentElse",
            int(self.pythonDedentElseCheckBox.isChecked()))
        Preferences.setEditorTyping("Python/DedentExcept",
            int(self.pythonDedentExceptCheckBox.isChecked()))
        Preferences.setEditorTyping("Python/Py24StyleTry",
            int(self.pythonDedentExceptPy24CheckBox.isChecked()))
        Preferences.setEditorTyping("Python/InsertImport",
            int(self.pythonInsertImportCheckBox.isChecked()))
        Preferences.setEditorTyping("Python/InsertSelf",
            int(self.pythonInsertSelfCheckBox.isChecked()))
        Preferences.setEditorTyping("Python/InsertBlank",
            int(self.pythonInsertBlankCheckBox.isChecked()))
        Preferences.setEditorTyping("Python/ColonDetection",
            int(self.pythonColonDetectionCheckBox.isChecked()))
        Preferences.setEditorTyping("Python/DedentDef",
            int(self.pythonDedentDefCheckBox.isChecked()))
        
        # Ruby
        Preferences.setEditorTyping("Ruby/EnabledTypingAids",
            int(self.rubyGroup.isChecked()))
        Preferences.setEditorTyping("Ruby/InsertClosingBrace",
            int(self.rubyInsertClosingBraceCheckBox.isChecked()))
        Preferences.setEditorTyping("Ruby/SkipBrace",
            int(self.rubySkipBraceCheckBox.isChecked()))
        Preferences.setEditorTyping("Ruby/IndentBrace",
            int(self.rubyIndentBraceCheckBox.isChecked()))
        Preferences.setEditorTyping("Ruby/InsertQuote",
            int(self.rubyInsertQuoteCheckBox.isChecked()))
        Preferences.setEditorTyping("Ruby/InsertBlank",
            int(self.rubyInsertBlankCheckBox.isChecked()))
        Preferences.setEditorTyping("Ruby/InsertHereDoc",
            int(self.rubyInsertHereDocCheckBox.isChecked()))
        Preferences.setEditorTyping("Ruby/InsertInlineDoc",
            int(self.rubyInsertInlineDocCheckBox.isChecked()))
        
    @pyqtSignature("QString")
    def on_languageCombo_activated(self, language):
        """
        Private slot to select the page related to the selected language.
        
        @param language name of the selected language (QString)
        """
        try:
            index = self.pageIds[str(language)]
        except KeyError:
            index = self.pageIds[' ']
        self.stackedWidget.setCurrentIndex(index)

def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorTypingPage()
    return page
