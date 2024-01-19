# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Icons configuration page.
"""

from PyQt4.QtCore import QDir, QString, QStringList, pyqtSignature
from PyQt4.QtGui import QListWidgetItem, QFileDialog

from KdeQt import KQFileDialog

from E4Gui.E4Completers import E4DirCompleter

from ConfigurationPageBase import ConfigurationPageBase
from IconsPreviewDialog import IconsPreviewDialog
from Ui_IconsPage import Ui_IconsPage

import Preferences
import Utilities

class IconsPage(ConfigurationPageBase, Ui_IconsPage):
    """
    Class implementing the Icons configuration page.
    """
    def __init__(self):
        """
        Constructor
        """
        ConfigurationPageBase.__init__(self)
        self.setupUi(self)
        self.setObjectName("IconsPage")
        
        self.iconDirectoryCompleter = E4DirCompleter(self.iconDirectoryEdit)
        
        # set initial values
        dirList = QStringList(Preferences.getIcons("Path"))
        for dir in dirList:
            if not dir.isEmpty():
                QListWidgetItem(dir, self.iconDirectoryList)
        
    def save(self):
        """
        Public slot to save the Icons configuration.
        """
        dirList = QStringList()
        for i in range(self.iconDirectoryList.count()):
            dirList.append(self.iconDirectoryList.item(i).text())
        Preferences.setIcons("Path", dirList)
        
    def on_iconDirectoryList_currentRowChanged(self, row):
        """
        Private slot to handle the currentRowChanged signal of the icons directory list.
        
        @param row the current row (integer)
        """
        if row == -1:
            self.deleteIconDirectoryButton.setEnabled(False)
            self.upButton.setEnabled(False)
            self.downButton.setEnabled(False)
            self.showIconsButton.setEnabled(\
                not self.iconDirectoryEdit.text().isEmpty())
        else:
            maxIndex = self.iconDirectoryList.count() - 1
            self.upButton.setEnabled(row != 0)
            self.downButton.setEnabled(row != maxIndex)
            self.deleteIconDirectoryButton.setEnabled(True)
            self.showIconsButton.setEnabled(True)
        
    def on_iconDirectoryEdit_textChanged(self, txt):
        """
        Private slot to handle the textChanged signal of the directory edit.
        
        @param txt the text of the directory edit (QString)
        """
        self.addIconDirectoryButton.setEnabled(not txt.isEmpty())
        self.showIconsButton.setEnabled(not txt.isEmpty() or \
            self.iconDirectoryList.currentRow() != -1)
        
    @pyqtSignature("")
    def on_upButton_clicked(self):
        """
        Private slot called to move the selected item up in the list.
        """
        row = self.iconDirectoryList.currentRow()
        if row == 0:
            # we're already at the top
            return
        
        itm = self.iconDirectoryList.takeItem(row)
        self.iconDirectoryList.insertItem(row - 1, itm)
        self.iconDirectoryList.setCurrentItem(itm)
        if row == 1:
            self.upButton.setEnabled(False)
        else:
            self.upButton.setEnabled(True)
        self.downButton.setEnabled(True)
        
    @pyqtSignature("")
    def on_downButton_clicked(self):
        """
        Private slot called to move the selected item down in the list.
        """
        rows = self.iconDirectoryList.count()
        row = self.iconDirectoryList.currentRow()
        if row == rows - 1:
            # we're already at the end
            return
        
        itm = self.iconDirectoryList.takeItem(row)
        self.iconDirectoryList.insertItem(row + 1, itm)
        self.iconDirectoryList.setCurrentItem(itm)
        self.upButton.setEnabled(True)
        if row == rows - 2:
            self.downButton.setEnabled(False)
        else:
            self.downButton.setEnabled(True)
        
    @pyqtSignature("")
    def on_iconDirectoryButton_clicked(self):
        """
        Private slot to select an icon directory.
        """
        dir = KQFileDialog.getExistingDirectory(\
            None,
            self.trUtf8("Select icon directory"),
            QString(),
            QFileDialog.Options(QFileDialog.ShowDirsOnly))
            
        if not dir.isEmpty():
            self.iconDirectoryEdit.setText(Utilities.toNativeSeparators(dir))
        
    @pyqtSignature("")
    def on_addIconDirectoryButton_clicked(self):
        """
        Private slot to add the icon directory displayed to the listbox.
        """
        dir = self.iconDirectoryEdit.text()
        if not dir.isEmpty():
            QListWidgetItem(dir, self.iconDirectoryList)
            self.iconDirectoryEdit.clear()
        row = self.iconDirectoryList.currentRow()
        self.on_iconDirectoryList_currentRowChanged(row)
        
    @pyqtSignature("")
    def on_deleteIconDirectoryButton_clicked(self):
        """
        Private slot to delete the currently selected directory of the listbox.
        """
        row = self.iconDirectoryList.currentRow()
        itm = self.iconDirectoryList.takeItem(row)
        del itm
        row = self.iconDirectoryList.currentRow()
        self.on_iconDirectoryList_currentRowChanged(row)
        
    @pyqtSignature("")
    def on_showIconsButton_clicked(self):
        """
        Private slot to display a preview of an icons directory.
        """
        dir = self.iconDirectoryEdit.text()
        if dir.isEmpty():
            itm = self.iconDirectoryList.currentItem()
            if itm is not None:
                dir = itm.text()
        if not dir.isEmpty():
            dlg = IconsPreviewDialog(self, dir)
            dlg.exec_()
    
def create(dlg):
    """
    Module function to create the configuration page.
    
    @param dlg reference to the configuration dialog
    """
    page = IconsPage()
    return page
