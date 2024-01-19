# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Spelling Properties dialog.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4FileCompleter

from QScintilla.SpellChecker import SpellChecker

from Ui_SpellingPropertiesDialog import Ui_SpellingPropertiesDialog

import Utilities
import Preferences

class SpellingPropertiesDialog(QDialog, Ui_SpellingPropertiesDialog):
    """
    Class implementing the Spelling Properties dialog.
    """
    def __init__(self, project, new, parent):
        """
        Constructor
        
        @param project reference to the project object
        @param new flag indicating the generation of a new project
        @param parent parent widget of this dialog (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.project = project
        self.parent = parent
        
        self.pwlCompleter = E4FileCompleter(self.pwlEdit)
        self.pelCompleter = E4FileCompleter(self.pelEdit)
        
        projectSpellings = QStringList(self.trUtf8("<default>"))
        for language in sorted(SpellChecker.getAvailableLanguages()):
            projectSpellings.append(language)
        self.spellingComboBox.addItems(projectSpellings)
        
        if not new:
            self.initDialog()
    
    def initDialog(self):
        """
        Public method to initialize the dialogs data.
        """
        index = self.spellingComboBox.findText(self.project.pdata["SPELLLANGUAGE"][0])
        if index == -1:
            index = 0
        self.spellingComboBox.setCurrentIndex(index)
        if self.project.pdata["SPELLWORDS"][0]:
            self.pwlEdit.setText(
                os.path.join(self.project.ppath, self.project.pdata["SPELLWORDS"][0]))
        if self.project.pdata["SPELLEXCLUDES"][0]:
            self.pelEdit.setText(
                os.path.join(self.project.ppath, self.project.pdata["SPELLEXCLUDES"][0]))
    
    @pyqtSignature("")
    def on_pwlButton_clicked(self):
        """
        Private slot to select the project word list file.
        """
        pwl = self.pwlEdit.text()
        if pwl.isEmpty():
            pwl = self.project.ppath
        file = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select project word list"),
            pwl,
            self.trUtf8("Dictionary File (*.dic);;All Files (*)"))
            
        if not file.isEmpty():
            self.pwlEdit.setText(Utilities.toNativeSeparators(file))
    
    @pyqtSignature("")
    def on_pelButton_clicked(self):
        """
        Private slot to select the project exclude list file.
        """
        pel = self.pelEdit.text()
        if pel.isEmpty():
            pel = self.project.ppath
        file = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select project exclude list"),
            pel,
            self.trUtf8("Dictionary File (*.dic);;All Files (*)"))
            
        if not file.isEmpty():
            self.pelEdit.setText(Utilities.toNativeSeparators(file))
    
    def storeData(self):
        """
        Public method to store the entered/modified data.
        """
        if self.spellingComboBox.currentIndex() == 0:
            self.project.pdata["SPELLLANGUAGE"] = \
                [Preferences.getEditor("SpellCheckingDefaultLanguage")]
        else:
            self.project.pdata["SPELLLANGUAGE"] = \
                [unicode(self.spellingComboBox.currentText())]
        self.project.pdata["SPELLWORDS"] = \
            [unicode(self.pwlEdit.text()).replace(self.project.ppath+os.sep, "")]
        self.project.pdata["SPELLEXCLUDES"] = \
            [unicode(self.pelEdit.text()).replace(self.project.ppath+os.sep, "")]
