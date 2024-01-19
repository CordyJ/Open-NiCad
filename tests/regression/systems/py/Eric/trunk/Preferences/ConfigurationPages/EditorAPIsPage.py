# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor APIs configuration page.
"""

from PyQt4.QtCore import QDir, QString, QStringList, pyqtSignature, SIGNAL, QFileInfo

from KdeQt import KQFileDialog, KQInputDialog
from KdeQt.KQApplication import e4App

from E4Gui.E4Completers import E4FileCompleter

from ConfigurationPageBase import ConfigurationPageBase
from Ui_EditorAPIsPage import Ui_EditorAPIsPage

from QScintilla.APIsManager import APIsManager
import QScintilla.Lexers

import Preferences
import Utilities

class EditorAPIsPage(ConfigurationPageBase, Ui_EditorAPIsPage):
    """
    Class implementing the Editor APIs configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("EditorAPIsPage")
        
        self.prepareApiButton.setText(self.trUtf8("Compile APIs"))
        self.__apisManager = APIsManager()
        self.__currentAPI = None
        self.__inPreparation = False
        
        self.apiFileCompleter = E4FileCompleter(self.apiFileEdit)
        
        # set initial values
        self.pluginManager = e4App().getObject("PluginManager")
        self.apiAutoPrepareCheckBox.setChecked(\
            Preferences.getEditor("AutoPrepareAPIs"))
        
        self.apis = {}
        apiLanguages = [''] + QScintilla.Lexers.getSupportedLanguages().keys()
        apiLanguages.sort()
        for lang in apiLanguages:
            if lang != "Guessed":
                self.apiLanguageComboBox.addItem(lang)
        self.currentApiLanguage = QString('')
        self.on_apiLanguageComboBox_activated(self.currentApiLanguage)
        
        for lang in apiLanguages[1:]:
            self.apis[lang] = QStringList(Preferences.getEditorAPI(lang))
        
    def save(self):
        """
        Public slot to save the Editor APIs configuration.
        """
        Preferences.setEditor("AutoPrepareAPIs",
            int(self.apiAutoPrepareCheckBox.isChecked()))
        
        lang = self.apiLanguageComboBox.currentText()
        self.apis[unicode(lang)] = self.__editorGetApisFromApiList()
        
        for lang, apis in self.apis.items():
            Preferences.setEditorAPI(lang, apis)
        
    @pyqtSignature("QString")
    def on_apiLanguageComboBox_activated(self, language):
        """
        Private slot to fill the api listbox of the api page.
        
        @param language selected API language (QString)
        """
        if self.currentApiLanguage.compare(language) == 0:
            return
            
        self.apis[unicode(self.currentApiLanguage)] = self.__editorGetApisFromApiList()
        self.currentApiLanguage = QString(language)
        self.apiList.clear()
        
        if language.isEmpty():
            self.apiGroup.setEnabled(False)
            return
            
        self.apiGroup.setEnabled(True)
        for api in self.apis[unicode(self.currentApiLanguage)]:
            if not api.isEmpty():
                self.apiList.addItem(api)
        self.__currentAPI = self.__apisManager.getAPIs(self.currentApiLanguage)
        if self.__currentAPI is not None:
            self.connect(self.__currentAPI, SIGNAL('apiPreparationFinished()'),
                         self.__apiPreparationFinished)
            self.connect(self.__currentAPI, SIGNAL('apiPreparationCancelled()'),
                         self.__apiPreparationCancelled)
            self.connect(self.__currentAPI, SIGNAL('apiPreparationStarted()'),
                         self.__apiPreparationStarted)
            self.addInstalledApiFileButton.setEnabled(\
                not self.__currentAPI.installedAPIFiles().isEmpty())
        else:
            self.addInstalledApiFileButton.setEnabled(False)
        
        self.addPluginApiFileButton.setEnabled(
            len(self.pluginManager.getPluginApiFiles(self.currentApiLanguage)) > 0)
        
    def __editorGetApisFromApiList(self):
        """
        Private slot to retrieve the api filenames from the list.
        
        @return list of api filenames (QStringList)
        """
        apis = QStringList()
        for row in range(self.apiList.count()):
            apis.append(self.apiList.item(row).text())
        return apis
        
    @pyqtSignature("")
    def on_apiFileButton_clicked(self):
        """
        Private method to select an api file.
        """
        file = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select API file"),
            self.apiFileEdit.text(),
            self.trUtf8("API File (*.api);;All Files (*)"))
            
        if not file.isEmpty():
            self.apiFileEdit.setText(Utilities.toNativeSeparators(file))
        
    @pyqtSignature("")
    def on_addApiFileButton_clicked(self):
        """
        Private slot to add the api file displayed to the listbox.
        """
        file = self.apiFileEdit.text()
        if not file.isEmpty():
            self.apiList.addItem(Utilities.toNativeSeparators(file))
            self.apiFileEdit.clear()
        
    @pyqtSignature("")
    def on_deleteApiFileButton_clicked(self):
        """
        Private slot to delete the currently selected file of the listbox.
        """
        crow = self.apiList.currentRow()
        if crow >= 0:
            itm = self.apiList.takeItem(crow)
            del itm
        
    @pyqtSignature("")
    def on_addInstalledApiFileButton_clicked(self):
        """
        Private slot to add an API file from the list of installed API files
        for the selected lexer language.
        """
        installedAPIFiles = self.__currentAPI.installedAPIFiles()
        installedAPIFilesPath = QFileInfo(installedAPIFiles[0]).path()
        installedAPIFilesShort = QStringList()
        for installedAPIFile in installedAPIFiles:
            installedAPIFilesShort.append(QFileInfo(installedAPIFile).fileName())
        file, ok = KQInputDialog.getItem(\
            self,
            self.trUtf8("Add from installed APIs"),
            self.trUtf8("Select from the list of installed API files"),
            installedAPIFilesShort,
            0, False)
        if ok:
            self.apiList.addItem(Utilities.toNativeSeparators(\
                QFileInfo(QDir(installedAPIFilesPath), file).absoluteFilePath()))
        
    @pyqtSignature("")
    def on_addPluginApiFileButton_clicked(self):
        """
        Private slot to add an API file from the list of API files installed
        by plugins for the selected lexer language.
        """
        pluginAPIFiles = self.pluginManager.getPluginApiFiles(self.currentApiLanguage)
        pluginAPIFilesDict = {}
        for apiFile in pluginAPIFiles:
            pluginAPIFilesDict[unicode(QFileInfo(apiFile).fileName())] = apiFile
        file, ok = KQInputDialog.getItem(\
            self,
            self.trUtf8("Add from Plugin APIs"),
            self.trUtf8(
                "Select from the list of API files installed by plugins"),
            sorted(pluginAPIFilesDict.keys()),
            0, False)
        if ok:
            self.apiList.addItem(Utilities.toNativeSeparators(\
                pluginAPIFilesDict[unicode(file)]))
        
    @pyqtSignature("")
    def on_prepareApiButton_clicked(self):
        """
        Private slot to prepare the API file for the currently selected language.
        """
        if self.__inPreparation:
            self.__currentAPI and self.__currentAPI.cancelPreparation()
        else:
            if self.__currentAPI is not None:
                self.__currentAPI.prepareAPIs(\
                    ondemand = True, 
                    rawList = QStringList(self.__editorGetApisFromApiList()))
        
    def __apiPreparationFinished(self):
        """
        Private method called after the API preparation has finished.
        """
        self.prepareApiProgressBar.reset()
        self.prepareApiProgressBar.setRange(0, 100)
        self.prepareApiProgressBar.setValue(0)
        self.prepareApiButton.setText(self.trUtf8("Compile APIs"))
        self.__inPreparation = False
    
    def __apiPreparationCancelled(self):
        """
        Private slot called after the API preparation has been cancelled.
        """
        self.__apiPreparationFinished()
    
    def __apiPreparationStarted(self):
        """
        Private method called after the API preparation has started.
        """
        self.prepareApiProgressBar.setRange(0, 0)
        self.prepareApiProgressBar.setValue(0)
        self.prepareApiButton.setText(self.trUtf8("Cancel compilation"))
        self.__inPreparation = True
        
    def saveState(self):
        """
        Public method to save the current state of the widget.
        
        @return index of the selected lexer language (integer)
        """
        return self.apiLanguageComboBox.currentIndex()
        
    def setState(self, state):
        """
        Public method to set the state of the widget.
        
        @param state state data generated by saveState
        """
        self.apiLanguageComboBox.setCurrentIndex(state)
        self.on_apiLanguageComboBox_activated(self.apiLanguageComboBox.currentText())
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = EditorAPIsPage()
    return page
