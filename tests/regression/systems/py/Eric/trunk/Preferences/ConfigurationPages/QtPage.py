# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Qt configuration page.
"""

import sys

from PyQt4.QtCore import QDir, pyqtSignature
from PyQt4.QtGui import QFileDialog

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4DirCompleter

from ConfigurationPageBase import ConfigurationPageBase
from Ui_QtPage import Ui_QtPage

import Preferences
import Utilities

class QtPage(ConfigurationPageBase, Ui_QtPage):
    """
    Class implementing the Qt configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("QtPage")
        
        self.qt4Completer = E4DirCompleter(self.qt4Edit)
        self.qt4TransCompleter = E4DirCompleter(self.qt4TransEdit)
        
        if sys.platform != "darwin":
            self.qt4Group.hide()
        
        # set initial values
        self.qt4Edit.setText(Preferences.getQt("Qt4Dir"))
        self.qt4TransEdit.setText(Preferences.getQt("Qt4TranslationsDir"))
        self.qt4PrefixEdit.setText(Preferences.getQt("QtToolsPrefix4"))
        self.qt4PostfixEdit.setText(Preferences.getQt("QtToolsPostfix4"))
        self.__updateQt4Sample()
        
    def save(self):
        """
        Public slot to save the Qt configuration.
        """
        Preferences.setQt("Qt4Dir", self.qt4Edit.text())
        Preferences.setQt("Qt4TranslationsDir", self.qt4TransEdit.text())
        Preferences.setQt("QtToolsPrefix4", self.qt4PrefixEdit.text())
        Preferences.setQt("QtToolsPostfix4", self.qt4PostfixEdit.text())
        
    @pyqtSignature("")
    def on_qt4Button_clicked(self):
        """
        Private slot to handle the Qt4 directory selection.
        """
        dir = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Select Qt4 Directory"),
            self.qt4Edit.text(),
            QFileDialog.Options(QFileDialog.ShowDirsOnly))
            
        if not dir.isNull():
            self.qt4Edit.setText(Utilities.toNativeSeparators(dir))
        
    @pyqtSignature("")
    def on_qt4TransButton_clicked(self):
        """
        Private slot to handle the Qt4 translations directory selection.
        """
        dir = KQFileDialog.getExistingDirectory(\
            self,
            self.trUtf8("Select Qt4 Translations Directory"),
            self.qt4TransEdit.text(),
            QFileDialog.Options(QFileDialog.ShowDirsOnly))
            
        if not dir.isNull():
            self.qt4TransEdit.setText(Utilities.toNativeSeparators(dir))
        
    def __updateQt4Sample(self):
        """
        Private slot to update the Qt4 tools sample label.
        """
        self.qt4SampleLabel.setText(self.trUtf8("Sample: %1designer%2")\
            .arg(self.qt4PrefixEdit.text())\
            .arg(self.qt4PostfixEdit.text()))
    
    @pyqtSignature("QString")
    def on_qt4PrefixEdit_textChanged(self, txt):
        """
        Private slot to handle a change in the entered Qt directory.
        
        @param txt the entered string (QString)
        """
        self.__updateQt4Sample()
    
    @pyqtSignature("QString")
    def on_qt4PostfixEdit_textChanged(self, txt):
        """
        Private slot to handle a change in the entered Qt directory.
        
        @param txt the entered string (QString)
        """
        self.__updateQt4Sample()
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = QtPage()
    return page
