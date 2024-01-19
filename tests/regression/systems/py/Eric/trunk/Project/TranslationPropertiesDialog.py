# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Translations Properties dialog.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4FileCompleter, E4DirCompleter

from Ui_TranslationPropertiesDialog import Ui_TranslationPropertiesDialog

import Utilities

class TranslationPropertiesDialog(QDialog, Ui_TranslationPropertiesDialog):
    """
    Class implementing the Translations Properties dialog.
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
        
        self.transPatternCompleter = E4FileCompleter(self.transPatternEdit)
        self.transBinPathCompleter = E4DirCompleter(self.transBinPathEdit)
        self.exceptionCompleter = E4FileCompleter(self.exceptionEdit)
        
        self.initFilters()
        if not new:
            self.initDialog()
        
    def initFilters(self):
        """
        Public method to initialize the filters.
        """
        patterns = {
            "SOURCES"    : QStringList(), 
            "FORMS"      : QStringList(), 
        }
        for pattern, filetype in self.project.pdata["FILETYPES"].items():
            if patterns.has_key(filetype):
                patterns[filetype].append(QString(pattern))
        self.filters = self.trUtf8("Source Files (%1);;")\
            .arg(patterns["SOURCES"].join(" "))
        if self.parent.getProjectType() in ["Qt4", "E4Plugin", "Kde4", "PySide"]:
            self.filters.append(self.trUtf8("Forms Files (%1);;")\
                .arg(patterns["FORMS"].join(" ")))
        self.filters.append(self.trUtf8("All Files (*)"))
        
    def initDialog(self):
        """
        Public method to initialize the dialogs data.
        """
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        try:
            self.transPatternEdit.setText(os.path.join(\
                self.project.ppath, self.project.pdata["TRANSLATIONPATTERN"][0]))
        except IndexError:
            pass
        try:
            self.transBinPathEdit.setText(os.path.join(\
                self.project.ppath, self.project.pdata["TRANSLATIONSBINPATH"][0]))
        except IndexError:
            pass
        self.exceptionsList.clear()
        for texcept in self.project.pdata["TRANSLATIONEXCEPTIONS"]:
            if texcept:
                self.exceptionsList.addItem(texcept)
        
    @pyqtSignature("")
    def on_transPatternButton_clicked(self):
        """
        Private slot to display a file selection dialog.
        """
        tp = self.transPatternEdit.text()
        if tp.contains("%language%"):
            tp = tp.section("%language%", 0, 0)
        tsfile = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select translation file"),
            tp,
            QString(),
            None)
        
        if not tsfile.isEmpty():
            self.transPatternEdit.setText(Utilities.toNativeSeparators(tsfile))
        
    @pyqtSignature("QString")
    def on_transPatternEdit_textChanged(self, txt):
        """
        Private slot to check the translation pattern for correctness.
        
        @param txt text of the transPatternEdit lineedit (QString)
        """
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            txt.contains("%language%"))
        
    @pyqtSignature("")
    def on_transBinPathButton_clicked(self):
        """
        Private slot to display a directory selection dialog.
        """
        directory = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Select directory for binary translations"),
            self.transBinPathEdit.text(),
            QFileDialog.Options(QFileDialog.Option(0)))
        
        if not directory.isEmpty():
            self.transBinPathEdit.setText(Utilities.toNativeSeparators(directory))
        
    @pyqtSignature("")
    def on_deleteExceptionButton_clicked(self):
        """
        Private slot to delete the currently selected entry of the listwidget.
        """
        row = self.exceptionsList.currentRow()
        itm = self.exceptionsList.takeItem(row)
        del itm
        row = self.exceptionsList.currentRow()
        self.on_exceptionsList_currentRowChanged(row)
        
    @pyqtSignature("")
    def on_addExceptionButton_clicked(self):
        """
        Private slot to add the shown exception to the listwidget.
        """
        if self.project.ppath == '':
            ppath = self.parent.getPPath()
        else:
            ppath = self.project.ppath
        texcept = unicode(self.exceptionEdit.text())
        texcept = texcept.replace(ppath + os.sep, "")
        if texcept.endswith(os.sep):
            texcept = texcept[:-1]
        if texcept:
            QListWidgetItem(texcept, self.exceptionsList)
            self.exceptionEdit.clear()
        row = self.exceptionsList.currentRow()
        self.on_exceptionsList_currentRowChanged(row)
        
    @pyqtSignature("")
    def on_exceptFileButton_clicked(self):
        """
        Private slot to select a file to exempt from translation.
        """
        texcept = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Exempt file from translation"),
            self.project.ppath,
            self.filters,
            None)
        if not texcept.isEmpty():
            self.exceptionEdit.setText(Utilities.toNativeSeparators(texcept))
        
    @pyqtSignature("")
    def on_exceptDirButton_clicked(self):
        """
        Private slot to select a file to exempt from translation.
        """
        texcept = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Exempt directory from translation"),
            self.project.ppath,
            QFileDialog.Options(QFileDialog.ShowDirsOnly))
        if not texcept.isEmpty():
            self.exceptionEdit.setText(Utilities.toNativeSeparators(texcept))
        
    def on_exceptionsList_currentRowChanged(self, row):
        """
        Private slot to handle the currentRowChanged signal of the exceptions list.
        
        @param row the current row (integer)
        """
        if row == -1:
            self.deleteExceptionButton.setEnabled(False)
        else:
            self.deleteExceptionButton.setEnabled(True)
        
    def on_exceptionEdit_textChanged(self, txt):
        """
        Private slot to handle the textChanged signal of the exception edit.
        
        @param txt the text of the exception edit (QString)
        """
        self.addExceptionButton.setEnabled(not txt.isEmpty())
        
    def storeData(self):
        """
        Public method to store the entered/modified data.
        """
        tp = Utilities.toNativeSeparators(self.transPatternEdit.text())
        if not tp.isEmpty():
            tp = unicode(tp).replace(self.project.ppath+os.sep, "")
            self.project.pdata["TRANSLATIONPATTERN"] = [tp]
            self.project.translationsRoot = tp.split("%language%")[0]
        else:
            self.project.pdata["TRANSLATIONPATTERN"] = []
        tp = Utilities.toNativeSeparators(self.transBinPathEdit.text())
        if not tp.isEmpty():
            tp = unicode(tp).replace(self.project.ppath+os.sep, "")
            self.project.pdata["TRANSLATIONSBINPATH"] = [tp]
        else:
            self.project.pdata["TRANSLATIONSBINPATH"] = []
        exceptList = []
        for i in range(self.exceptionsList.count()):
            exceptList.append(unicode(self.exceptionsList.item(i).text()))
        self.project.pdata["TRANSLATIONEXCEPTIONS"] = exceptList[:]
