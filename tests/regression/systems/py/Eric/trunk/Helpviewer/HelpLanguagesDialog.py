# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to configure the preferred languages.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_HelpLanguagesDialog import Ui_HelpLanguagesDialog

import Preferences

class HelpLanguagesDialog(QDialog, Ui_HelpLanguagesDialog):
    """
    Class implementing a dialog to configure the preferred languages.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.__model = QStringListModel()
        self.languagesList.setModel(self.__model)
        self.connect(self.languagesList.selectionModel(), 
            SIGNAL("currentChanged(const QModelIndex&, const QModelIndex&)"), 
            self.__currentChanged)
        
        languages = Preferences.Prefs.settings.value(
            "Help/AcceptLanguages", QVariant(self.defaultAcceptLanguages()))\
            .toStringList()
        self.__model.setStringList(languages)
        
        allLanguages = QStringList()
        for index in range(QLocale.C + 1, QLocale.LastLanguage + 1):
            allLanguages += self.expand(QLocale.Language(index))
        self.__allLanguagesModel = QStringListModel()
        self.__allLanguagesModel.setStringList(allLanguages)
        self.addCombo.setModel(self.__allLanguagesModel)
    
    def __currentChanged(self, current, previous):
        """
        Private slot to handle a change of the current selection.
        
        @param current index of the currently selected item (QModelIndex)
        @param previous index of the previously selected item (QModelIndex)
        """
        self.removeButton.setEnabled(current.isValid())
        row = current.row()
        self.upButton.setEnabled(row > 0)
        self.downButton.setEnabled(row != -1 and row < self.__model.rowCount() - 1)

    @pyqtSignature("")
    def on_upButton_clicked(self):
        """
        Private slot to move a language up.
        """
        currentRow = self.languagesList.currentIndex().row()
        data = self.languagesList.currentIndex().data()
        self.__model.removeRow(currentRow)
        self.__model.insertRow(currentRow - 1)
        self.__model.setData(self.__model.index(currentRow - 1), data)
        self.languagesList.setCurrentIndex(self.__model.index(currentRow - 1))
    
    @pyqtSignature("")
    def on_downButton_clicked(self):
        """
        Private slot to move a language down.
        """
        currentRow = self.languagesList.currentIndex().row()
        data = self.languagesList.currentIndex().data()
        self.__model.removeRow(currentRow)
        self.__model.insertRow(currentRow + 1)
        self.__model.setData(self.__model.index(currentRow + 1), data)
        self.languagesList.setCurrentIndex(self.__model.index(currentRow + 1))
    
    @pyqtSignature("")
    def on_removeButton_clicked(self):
        """
        Private slot to remove a language from the list of acceptable languages.
        """
        currentRow = self.languagesList.currentIndex().row()
        self.__model.removeRow(currentRow)
    
    @pyqtSignature("")
    def on_addButton_clicked(self):
        """
        Private slot to add a language to the list of acceptable languages.
        """
        language = self.addCombo.currentText()
        if language in self.__model.stringList():
            return
        
        self.__model.insertRow(self.__model.rowCount())
        self.__model.setData(self.__model.index(self.__model.rowCount() - 1), 
                             QVariant(language))
        self.languagesList.setCurrentIndex(
            self.__model.index(self.__model.rowCount() - 1))
    
    def accept(self):
        """
        Public method to accept the data entered.
        """
        result = self.__model.stringList()
        if result == self.defaultAcceptLanguages():
            Preferences.Prefs.settings.remove("Help/AcceptLanguages")
        else:
            Preferences.Prefs.settings.setValue("Help/AcceptLanguages", QVariant(result))
        QDialog.accept(self)
    
    @classmethod
    def httpString(cls, languages):
        """
        Class method to convert a list of acceptable languages into a byte array that
        can be sent along with the Accept-Language http header (see RFC 2616).
        
        @param languages list of acceptable languages (QStringList)
        @return converted list (QByteArray)
        """
        processed = QStringList()
        qvalue = 1.0
        for language in languages:
            leftBracket = language.indexOf('[')
            rightBracket = language.indexOf(']')
            tag = language.mid(leftBracket + 1, rightBracket - leftBracket - 1)
            if processed.isEmpty():
                processed.append(tag)
            else:
                processed.append(
                    QString("%1;q=%2").arg(tag).arg(QString.number(qvalue, 'f', 1)))
            if qvalue > 0.1:
                qvalue -= 0.1
        
        return processed.join(", ").toLatin1()
    
    @classmethod
    def defaultAcceptLanguages(cls):
        """
        Class method to get the list of default accept languages.
        
        @return list of acceptable languages (QStringList)
        """
        language = QLocale.system().name()
        if language.isEmpty():
            return QStringList()
        else:
            return cls.expand(QLocale(language).language())
    
    @classmethod
    def expand(self, language):
        """
        Class method to expand a language enum to a readable languages list.
        
        @param language language number (QLocale.Language)
        @return list of expanded language names (QStringList)
        """
        allLanguages = QStringList()
        countries = QLocale.countriesForLanguage(language)
        languageString = QString("%1 [%2]")\
            .arg(QLocale.languageToString(language))\
            .arg(QLocale(language).name().split('_')[0])
        allLanguages.append(languageString)
        for country in countries:
            languageString = QString("%1/%2 [%3]")\
                .arg(QLocale.languageToString(language))\
                .arg(QLocale.countryToString(country))\
                .arg(QLocale(language, country).name().split('_').join('-').toLower())
            if languageString not in allLanguages:
                allLanguages.append(languageString)
        
        return allLanguages
