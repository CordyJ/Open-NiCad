# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the project properties dialog.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt import KQFileDialog
from KdeQt.KQApplication import e4App

from E4Gui.E4Completers import E4FileCompleter, E4DirCompleter

from Ui_PropertiesDialog import Ui_PropertiesDialog
from TranslationPropertiesDialog import TranslationPropertiesDialog
from SpellingPropertiesDialog import SpellingPropertiesDialog

from VCS.RepositoryInfoDialog import VcsRepositoryInfoDialog

import Preferences
import Utilities

class PropertiesDialog(QDialog, Ui_PropertiesDialog):
    """
    Class implementing the project properties dialog.
    """
    def __init__(self, project, new = True, parent = None, name = None):
        """
        Constructor
        
        @param project reference to the project object
        @param new flag indicating the generation of a new project
        @param parent parent widget of this dialog (QWidget)
        @param name name of this dialog (string or QString)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)
        
        self.project = project
        self.newProject = new
        self.transPropertiesDlg = None
        self.spellPropertiesDlg = None
        
        self.dirCompleter = E4DirCompleter(self.dirEdit)
        self.mainscriptCompleter = E4FileCompleter(self.mainscriptEdit)
        
        projectLanguages = QStringList()
        for language in e4App().getObject("DebugServer").getSupportedLanguages():
            projectLanguages.append(language)
        projectLanguages.sort()
        self.languageComboBox.addItems(projectLanguages)
        
        projectTypes = project.getProjectTypes()
        for projectTypeKey in sorted(projectTypes.keys()):
            self.projectTypeComboBox.addItem(projectTypes[projectTypeKey], 
                                        QVariant(projectTypeKey))
        
        if not new:
            name = os.path.splitext(self.project.pfile)[0]
            self.nameEdit.setText(os.path.basename(name))
            self.languageComboBox.setCurrentIndex(\
                self.languageComboBox.findText(self.project.pdata["PROGLANGUAGE"][0]))
            self.mixedLanguageCheckBox.setChecked(self.project.pdata["MIXEDLANGUAGE"][0])
            try:
                curIndex = \
                    self.projectTypeComboBox.findText(\
                        projectTypes[self.project.pdata["PROJECTTYPE"][0]])
            except KeyError:
                curIndex = -1
            if curIndex == -1:
                curIndex = self.projectTypeComboBox.findText(projectTypes["Qt4"])
            self.projectTypeComboBox.setCurrentIndex(curIndex)
            self.dirEdit.setText(self.project.ppath)
            try:
                self.versionEdit.setText(self.project.pdata["VERSION"][0])
            except IndexError:
                pass
            try:
                self.mainscriptEdit.setText(self.project.pdata["MAINSCRIPT"][0])
            except IndexError:
                pass
            try:
                self.authorEdit.setText(self.project.pdata["AUTHOR"][0])
            except IndexError:
                pass
            try:
                self.emailEdit.setText(self.project.pdata["EMAIL"][0])
            except IndexError:
                pass
            try:
                self.descriptionEdit.setPlainText(self.project.pdata["DESCRIPTION"][0])
            except LookupError:
                pass
            self.vcsLabel.show()
            if self.project.vcs is not None:
                vcsSystemsDict = e4App().getObject("PluginManager")\
                    .getPluginDisplayStrings("version_control")
                try:
                    vcsSystemDisplay = vcsSystemsDict[self.project.pdata["VCS"][0]]
                except KeyError:
                    vcsSystemDisplay = "None"
                self.vcsLabel.setText(\
                    self.trUtf8("The project is version controlled by <b>%1</b>.")
                    .arg(vcsSystemDisplay))
                self.vcsInfoButton.show()
            else:
                self.vcsLabel.setText(\
                    self.trUtf8("The project is not version controlled."))
                self.vcsInfoButton.hide()
        else:
            self.projectTypeComboBox.setCurrentIndex(\
                self.projectTypeComboBox.findText(projectTypes["Qt4"]))
            hp = os.getcwd()
            hp = hp + os.sep
            self.dirEdit.setText(hp)
            self.versionEdit.setText('0.1')
            self.vcsLabel.hide()
            self.vcsInfoButton.hide()
        
    @pyqtSignature("")
    def on_dirButton_clicked(self):
        """
        Private slot to display a directory selection dialog.
        """
        directory = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Select project directory"),
            self.dirEdit.text(),
            QFileDialog.Options(QFileDialog.ShowDirsOnly))
        
        if not directory.isEmpty():
            self.dirEdit.setText(Utilities.toNativeSeparators(directory))
        
    @pyqtSignature("")
    def on_spellPropertiesButton_clicked(self):
        """
        Private slot to display the spelling properties dialog.
        """
        if self.spellPropertiesDlg is None:
            self.spellPropertiesDlg = \
                SpellingPropertiesDialog(self.project, self.newProject, self)
        res = self.spellPropertiesDlg.exec_()
        if res == QDialog.Rejected:
            self.spellPropertiesDlg.initDialog() # reset the dialogs contents
        
    @pyqtSignature("")
    def on_transPropertiesButton_clicked(self):
        """
        Private slot to display the translations properties dialog.
        """
        if self.transPropertiesDlg is None:
            self.transPropertiesDlg = \
                TranslationPropertiesDialog(self.project, self.newProject, self)
        else:
            self.transPropertiesDlg.initFilters()
        res = self.transPropertiesDlg.exec_()
        if res == QDialog.Rejected:
            self.transPropertiesDlg.initDialog() # reset the dialogs contents
        
    @pyqtSignature("")
    def on_mainscriptButton_clicked(self):
        """
        Private slot to display a file selection dialog.
        """
        dir = self.dirEdit.text()
        if dir.isEmpty():
            dir = QDir.currentPath()
        patterns = QStringList()
        for pattern, filetype in self.project.pdata["FILETYPES"].items():
            if filetype == "SOURCES":
                patterns.append(QString(pattern))
        filters = self.trUtf8("Source Files (%1);;All Files (*)")\
            .arg(patterns.join(" "))
        fn = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select main script file"),
            dir,
            filters)
        
        if not fn.isEmpty():
            ppath = self.dirEdit.text()
            if not ppath.isEmpty():
                ppath = QDir(ppath).absolutePath()
                ppath.append(QDir.separator())
                fn.replace(QRegExp(ppath), "")
            self.mainscriptEdit.setText(Utilities.toNativeSeparators(fn))
        
    @pyqtSignature("")
    def on_vcsInfoButton_clicked(self):
        """
        Private slot to display a vcs information dialog.
        """
        if self.project.vcs is None:
            return
            
        info = self.project.vcs.vcsRepositoryInfos(self.project.ppath)
        dlg = VcsRepositoryInfoDialog(self, info)
        dlg.exec_()
        
    def getProjectType(self):
        """
        Public method to get the selected project type.
        
        @return selected UI type (string)
        """
        data = self.projectTypeComboBox.itemData(self.projectTypeComboBox.currentIndex())
        return str(data.toString())
        
    def getPPath(self):
        """
        Public method to get the project path.
        
        @return data of the project directory edit (string)
        """
        return os.path.abspath(unicode(self.dirEdit.text()))
        
    def storeData(self):
        """
        Public method to store the entered/modified data.
        """
        self.project.ppath = os.path.abspath(unicode(self.dirEdit.text()))
        fn = self.nameEdit.text()
        if not fn.isEmpty():
            self.project.name = unicode(fn)
            if Preferences.getProject("CompressedProjectFiles"):
                fn = "%s.e4pz" % unicode(fn)
            else:
                fn = "%s.e4p" % unicode(fn)
            self.project.pfile = os.path.join(self.project.ppath, fn)
        else:
            self.project.pfile = ""
        self.project.pdata["VERSION"] = [unicode(self.versionEdit.text())]
        fn = self.mainscriptEdit.text()
        if not fn.isEmpty():
            fn = unicode(fn).replace(self.project.ppath+os.sep, "")
            self.project.pdata["MAINSCRIPT"] = [fn]
            self.project.translationsRoot = os.path.splitext(fn)[0]
        else:
            self.project.pdata["MAINSCRIPT"] = []
            self.project.translationsRoot = ""
        self.project.pdata["AUTHOR"] = [unicode(self.authorEdit.text())]
        self.project.pdata["EMAIL"] = [unicode(self.emailEdit.text())]
        self.project.pdata["DESCRIPTION"] = [unicode(self.descriptionEdit.toPlainText())]
        self.project.pdata["PROGLANGUAGE"] = \
            [unicode(self.languageComboBox.currentText())]
        self.project.pdata["MIXEDLANGUAGE"] = [self.mixedLanguageCheckBox.isChecked()]
        projectType = self.getProjectType()
        if projectType is not None:
            self.project.pdata["PROJECTTYPE"] = [projectType]
        
        if self.spellPropertiesDlg is not None:
            self.spellPropertiesDlg.storeData()
        
        if self.transPropertiesDlg is not None:
            self.transPropertiesDlg.storeData()
