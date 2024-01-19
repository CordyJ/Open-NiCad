# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Interface configuration page.
"""

import glob
import os

from PyQt4.QtCore import pyqtSignature, QVariant, QTranslator, QString, qVersion
from PyQt4.QtGui import QStyleFactory

from E4Gui.E4Completers import E4FileCompleter

from ConfigurationPageBase import ConfigurationPageBase
from Ui_InterfacePage import Ui_InterfacePage

from KdeQt import KQFileDialog
import KdeQt

import Preferences
import Utilities

from eric4config import getConfig

class InterfacePage(ConfigurationPageBase, Ui_InterfacePage):
    """
    Class implementing the Interface configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("InterfacePage")
        
        self.styleSheetCompleter = E4FileCompleter(self.styleSheetEdit)
        
        self.uiColours = {}
        
        # set initial values
        self.__populateStyleCombo()
        self.__populateLanguageCombo()
        
        self.uiBrowsersListFoldersFirstCheckBox.setChecked(
            Preferences.getUI("BrowsersListFoldersFirst"))
        self.uiBrowsersHideNonPublicCheckBox.setChecked(
            Preferences.getUI("BrowsersHideNonPublic"))
        self.uiBrowsersSortByOccurrenceCheckBox.setChecked(
            Preferences.getUI("BrowsersListContentsByOccurrence"))
        
        self.lvAutoRaiseCheckBox.setChecked(
            Preferences.getUI("LogViewerAutoRaise"))
        
        self.uiCaptionShowsFilenameGroupBox.setChecked(
            Preferences.getUI("CaptionShowsFilename"))
        self.filenameLengthSpinBox.setValue(\
            Preferences.getUI("CaptionFilenameLength"))
        self.styleSheetEdit.setText(Preferences.getUI("StyleSheet"))
        
        if Preferences.getUI("TopLeftByLeft"):
            self.tlLeftButton.setChecked(True)
        else:
            self.tlTopButton.setChecked(True)
        if Preferences.getUI("BottomLeftByLeft"):
            self.blLeftButton.setChecked(True)
        else:
            self.blBottomButton.setChecked(True)
        if Preferences.getUI("TopRightByRight"):
            self.trRightButton.setChecked(True)
        else:
            self.trTopButton.setChecked(True)
        if Preferences.getUI("BottomRightByRight"):
            self.brRightButton.setChecked(True)
        else:
            self.brTopButton.setChecked(True)
        
        layout = Preferences.getUILayout()
        if layout[0] == "DockWindows":
            index = 0
        elif layout[0] == "FloatingWindows":
            index = 1
        elif layout[0] == "Toolboxes":
            index = 2
        elif layout[0] == "Sidebars":
            index = 3
        else:
            index = 0   # default for bad values
        self.layoutComboBox.setCurrentIndex(index)
        if layout[1] == 0:
            self.separateShellButton.setChecked(True)
        else:
            self.debugEmbeddedShellButton.setChecked(True)
        if layout[2] == 0:
            self.separateFileBrowserButton.setChecked(True)
        elif layout[2] == 1:
            self.debugEmbeddedFileBrowserButton.setChecked(True)
        else:
            self.projectEmbeddedFileBrowserButton.setChecked(True)
        
        if qVersion() < '4.5.0':
            self.tabsGroupBox.setEnabled(False)
            self.tabsCloseButtonCheckBox.setChecked(True)
        else:
            self.tabsGroupBox.setEnabled(True)
            self.tabsCloseButtonCheckBox.setChecked(
                Preferences.getUI("SingleCloseButton"))
        
        self.uiKdeDialogsCheckBox.setChecked(\
            Preferences.getUI("UseKDEDialogs"))
        
        self.uiColours["LogStdErrColour"] = \
            self.initColour("LogStdErrColour", self.stderrTextColourButton, 
                Preferences.getUI)
        
    def save(self):
        """
        Public slot to save the Interface configuration.
        """
        # save the style settings
        styleIndex = self.styleComboBox.currentIndex()
        style = self.styleComboBox.itemData(styleIndex).toString()
        Preferences.setUI("Style", style)
        
        # save the other UI related settings
        Preferences.setUI("BrowsersListFoldersFirst",
            int(self.uiBrowsersListFoldersFirstCheckBox.isChecked()))
        Preferences.setUI("BrowsersHideNonPublic",
            int(self.uiBrowsersHideNonPublicCheckBox.isChecked()))
        Preferences.setUI("BrowsersListContentsByOccurrence", 
            int(self.uiBrowsersSortByOccurrenceCheckBox.isChecked()))
        Preferences.setUI("LogViewerAutoRaise", 
            int(self.lvAutoRaiseCheckBox.isChecked()))
        Preferences.setUI("CaptionShowsFilename",
            int(self.uiCaptionShowsFilenameGroupBox.isChecked()))
        Preferences.setUI("CaptionFilenameLength",
            self.filenameLengthSpinBox.value())
        Preferences.setUI("StyleSheet",
            self.styleSheetEdit.text())
        
        # save the dockarea corner settings
        Preferences.setUI("TopLeftByLeft", 
            int(self.tlLeftButton.isChecked()))
        Preferences.setUI("BottomLeftByLeft", 
            int(self.blLeftButton.isChecked()))
        Preferences.setUI("TopRightByRight", 
            int(self.trRightButton.isChecked()))
        Preferences.setUI("BottomRightByRight", 
            int(self.brRightButton.isChecked()))
        
        # save the language settings
        uiLanguageIndex = self.languageComboBox.currentIndex()
        if uiLanguageIndex:
            uiLanguage = unicode(\
                self.languageComboBox.itemData(uiLanguageIndex).toString())
        else:
            uiLanguage = None
        Preferences.setUILanguage(uiLanguage)
        
        # save the interface layout settings
        if self.separateShellButton.isChecked():
            layout2 = 0
        else:
            layout2 = 1
        if self.separateFileBrowserButton.isChecked():
            layout3 = 0
        elif self.debugEmbeddedFileBrowserButton.isChecked():
            layout3 = 1
        else:
            layout3 = 2
        if self.layoutComboBox.currentIndex() == 0:
            layout1 = "DockWindows"
        elif self.layoutComboBox.currentIndex() == 1:
            layout1 = "FloatingWindows"
        elif self.layoutComboBox.currentIndex() == 2:
            layout1 = "Toolboxes"
        elif self.layoutComboBox.currentIndex() == 3:
            layout1 = "Sidebars"
        else:
            layout1 = "DockWindows"
        layout = (layout1, layout2, layout3)
        Preferences.setUILayout(layout)
        
        Preferences.setUI("SingleCloseButton", 
            int(self.tabsCloseButtonCheckBox.isChecked()))
        
        Preferences.setUI("UseKDEDialogs",
            int(self.uiKdeDialogsCheckBox.isChecked()))
        
        for key in self.uiColours.keys():
            Preferences.setUI(key, self.uiColours[key])
        
    def __populateStyleCombo(self):
        """
        Private method to populate the style combo box.
        """
        curStyle = Preferences.getUI("Style")
        styles = QStyleFactory.keys()
        styles.sort()
        self.styleComboBox.addItem(self.trUtf8('System'), QVariant("System"))
        for style in styles:
            self.styleComboBox.addItem(style, QVariant(style))
        currentIndex = self.styleComboBox.findData(QVariant(curStyle))
        if currentIndex == -1:
            currentIndex = 0
        self.styleComboBox.setCurrentIndex(currentIndex)
        
    def __populateLanguageCombo(self):
        """
        Private method to initialize the language combobox of the Interface 
        configuration page.
        """
        self.languageComboBox.clear()
        
        fnlist = glob.glob("eric4_*.qm") + \
            glob.glob(os.path.join(getConfig('ericTranslationsDir'), "eric4_*.qm")) + \
            glob.glob(os.path.join(Utilities.getConfigDir(), "eric4_*.qm"))
        locales = {}
        for fn in fnlist:
            locale = os.path.basename(fn)[6:-3]
            if not locales.has_key(locale):
                translator = QTranslator()
                translator.load(fn)
                locales[locale] = \
                    translator.translate("InterfacePage", "English", 
                                         "Translate this with your language") + \
                    QString(" (%1)").arg(locale)
        localeList = locales.keys()
        localeList.sort()
        
        try:
            uiLanguage = unicode(Preferences.getUILanguage())
            if uiLanguage == "None":
                currentIndex = 0
            elif uiLanguage == "System":
                currentIndex = 1
            else:
                currentIndex = localeList.index(uiLanguage) + 2
        except ValueError:
            currentIndex = 0
        self.languageComboBox.clear()
        
        self.languageComboBox.addItem("English (default)", QVariant("None"))
        self.languageComboBox.addItem(self.trUtf8('System'), QVariant("System"))
        for locale in localeList:
            self.languageComboBox.addItem(locales[locale], QVariant(locale))
        self.languageComboBox.setCurrentIndex(currentIndex)
        
    @pyqtSignature("")
    def on_styleSheetButton_clicked(self):
        """
        Private method to select the style sheet file via a dialog.
        """
        file = KQFileDialog.getOpenFileName(\
            self,
            self.trUtf8("Select style sheet file"),
            self.styleSheetEdit.text(),
            self.trUtf8("Qt Style Sheets (*.qss);;Cascading Style Sheets (*.css);;"
                        "All files (*)"),
            None)
        
        if not file.isEmpty():
            self.styleSheetEdit.setText(Utilities.toNativeSeparators(file))
        
    @pyqtSignature("")
    def on_resetLayoutButton_clicked(self):
        """
        Private method to reset layout to factory defaults
        """
        Preferences.resetLayout()
        
    @pyqtSignature("")
    def on_stderrTextColourButton_clicked(self):
        """
        Private slot to set the foreground colour of the caret.
        """
        self.uiColours["LogStdErrColour"] = \
            self.selectColour(self.stderrTextColourButton, 
                self.uiColours["LogStdErrColour"])
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = InterfacePage()
    return page
