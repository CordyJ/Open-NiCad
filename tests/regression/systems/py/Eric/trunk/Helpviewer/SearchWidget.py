# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the search bar for the web browser.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_SearchWidget import Ui_SearchWidget

import UI.PixmapCache

class SearchWidget(QWidget, Ui_SearchWidget):
    """
    Class implementing the search bar for the web browser.
    """
    def __init__(self, mainWindow, parent = None):
        """
        Constructor
        
        @param mainWindow reference to the main window (QMainWindow)
        @param parent parent widget of this dialog (QWidget)
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.__mainWindow = mainWindow
        
        self.wrapCheckBox.setChecked(True)
        self.closeButton.setIcon(UI.PixmapCache.getIcon("close.png"))
        self.findPrevButton.setIcon(UI.PixmapCache.getIcon("1leftarrow.png"))
        self.findNextButton.setIcon(UI.PixmapCache.getIcon("1rightarrow.png"))
        
        self.__defaultBaseColor = \
            self.findtextCombo.lineEdit().palette().color(QPalette.Base)
        self.__defaultTextColor = \
            self.findtextCombo.lineEdit().palette().color(QPalette.Text)
        
        self.findHistory = QStringList()
        self.havefound = False
        self.__findBackwards = False
        
        self.connect(self.findtextCombo.lineEdit(), SIGNAL("returnPressed()"), 
                     self.__findByReturnPressed)

    def on_findtextCombo_editTextChanged(self, txt):
        """
        Private slot to enable/disable the find buttons.
        """
        self.findPrevButton.setEnabled(not txt.isEmpty())
        self.findNextButton.setEnabled(not txt.isEmpty())

    def __findNextPrev(self):
        """
        Private slot to find the next occurrence of text.
        """
        self.infoLabel.clear()
        self.__setFindtextComboBackground(False)
        
        if not self.havefound or self.findtextCombo.currentText().isEmpty():
            self.showFind()
            return
        
        if not self.__mainWindow.currentBrowser().findNextPrev(
                self.findtextCombo.currentText(), 
                self.caseCheckBox.isChecked(), 
                self.__findBackwards, 
                self.wrapCheckBox.isChecked()):
            self.infoLabel.setText(self.trUtf8("Expression was not found."))
            self.__setFindtextComboBackground(True)
    @pyqtSignature("")
    def on_findNextButton_clicked(self):
        """
        Private slot to find the next occurrence.
        """
        txt = self.findtextCombo.currentText()
        
        # This moves any previous occurrence of this statement to the head
        # of the list and updates the combobox
        self.findHistory.removeAll(txt)
        self.findHistory.prepend(txt)
        self.findtextCombo.clear()
        self.findtextCombo.addItems(self.findHistory)
        
        self.__findBackwards = False
        self.__findNextPrev()
    
    def findNext(self):
        """
        Public slot to find the next occurrence.
        """
        self.on_findNextButton_clicked()

    @pyqtSignature("")
    def on_findPrevButton_clicked(self):
        """
        Private slot to find the previous occurrence.
        """
        txt = self.findtextCombo.currentText()
        
        # This moves any previous occurrence of this statement to the head
        # of the list and updates the combobox
        self.findHistory.removeAll(txt)
        self.findHistory.prepend(txt)
        self.findtextCombo.clear()
        self.findtextCombo.addItems(self.findHistory)
        
        self.__findBackwards = True
        self.__findNextPrev()
    
    def findPrevious(self):
        """
        Public slot to find the previous occurrence.
        """
        self.on_findPrevButton_clicked()
    
    def __findByReturnPressed(self):
        """
        Private slot to handle the returnPressed signal of the findtext combobox.
        """
        if self.__findBackwards:
            self.on_findPrevButton_clicked()
        else:
            self.on_findNextButton_clicked()

    def showFind(self):
        """
        Public method to display this dialog.
        """
        self.havefound = True
        self.__findBackwards = False
        
        self.findtextCombo.clear()
        self.findtextCombo.addItems(self.findHistory)
        self.findtextCombo.setEditText('')
        self.findtextCombo.setFocus()
        
        self.caseCheckBox.setChecked(False)
        
        if self.__mainWindow.currentBrowser().hasSelection():
            self.findtextCombo.setEditText(
                self.__mainWindow.currentBrowser().selectedText())
        
        self.__setFindtextComboBackground(False)
        self.show()

    @pyqtSignature("")
    def on_closeButton_clicked(self):
        """
        Private slot to close the widget.
        """
        self.close()
    
    def keyPressEvent(self, event):
        """
        Protected slot to handle key press events.
        
        @param event reference to the key press event (QKeyEvent)
        """
        if event.key() == Qt.Key_Escape:
            cb = self.__mainWindow.currentBrowser()
            if cb:
                cb.setFocus(Qt.ActiveWindowFocusReason)
            event.accept()
            self.close()
    
    def __setFindtextComboBackground(self, error):
        """
        Private slot to change the findtext combo background to indicate errors.
        
        @param error flag indicating an error condition (boolean)
        """
        le = self.findtextCombo.lineEdit()
        p = le.palette()
        if error:
            p.setBrush(QPalette.Base, QBrush(QColor("#FF6666")))
            p.setBrush(QPalette.Text, QBrush(QColor("#FFFFFF")))
        else:
            p.setBrush(QPalette.Base, self.__defaultBaseColor)
            p.setBrush(QPalette.Text, self.__defaultTextColor)
        le.setPalette(p)
        le.update()
