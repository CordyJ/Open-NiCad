# -*- coding: utf-8 -*-

# Copyright (c) 2003 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog for the configuration of a keyboard shortcut.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_ShortcutDialog import Ui_ShortcutDialog


class ShortcutDialog(QDialog, Ui_ShortcutDialog):
    """
    Class implementing a dialog for the configuration of a keyboard shortcut.
    
    @signal shortcutChanged(QKeySequence, QKeySequence, bool, objectType) emitted 
        after the OK button was pressed
    """
    def __init__(self, parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setModal(modal)
        self.setupUi(self)
        
        self.keyIndex = 0
        self.keys = [0, 0, 0, 0]
        self.noCheck = False
        self.objectType = None
        
        self.connect(self.primaryClearButton, SIGNAL("clicked()"), self.__clear)
        self.connect(self.alternateClearButton, SIGNAL("clicked()"), self.__clear)
        self.connect(self.primaryButton, SIGNAL("clicked()"), self.__typeChanged)
        self.connect(self.alternateButton, SIGNAL("clicked()"), self.__typeChanged)
        
        self.shortcutsGroup.installEventFilter(self)
        self.primaryButton.installEventFilter(self)
        self.alternateButton.installEventFilter(self)
        self.primaryClearButton.installEventFilter(self)
        self.alternateClearButton.installEventFilter(self)
        
        self.buttonBox.button(QDialogButtonBox.Ok).installEventFilter(self)
        self.buttonBox.button(QDialogButtonBox.Cancel).installEventFilter(self)

    def setKeys(self, key, alternateKey,  noCheck, objectType):
        """
        Public method to set the key to be configured.
        
        @param key key sequence to be changed (QKeySequence)
        @param alternateKey alternate key sequence to be changed (QKeySequence)
        @param noCheck flag indicating that no uniqueness check should
            be performed (boolean)
        @param objectType type of the object (string).
        """
        self.keyIndex = 0
        self.keys = [0, 0, 0, 0]
        self.keyLabel.setText(QString(key))
        self.alternateKeyLabel.setText(QString(alternateKey))
        self.primaryButton.setChecked(True)
        self.noCheck = noCheck
        self.objectType = objectType
        
    def on_buttonBox_accepted(self):
        """
        Private slot to handle the OK button press.
        """
        self.hide()
        self.emit(SIGNAL('shortcutChanged'), 
                  QKeySequence(self.keyLabel.text()),
                  QKeySequence(self.alternateKeyLabel.text()), 
                  self.noCheck, self.objectType)

    def __clear(self):
        """
        Private slot to handle the Clear button press.
        """
        self.keyIndex = 0
        self.keys = [0, 0, 0, 0]
        self.__setKeyLabelText("")
        
    def __typeChanged(self):
        """
        Private slot to handle the change of the shortcuts type.
        """
        self.keyIndex = 0
        self.keys = [0, 0, 0, 0]
        
    def __setKeyLabelText(self, txt):
        """
        Private method to set the text of a key label.
        
        @param txt text to be set (QString)
        """
        if self.primaryButton.isChecked():
            self.keyLabel.setText(txt)
        else:
            self.alternateKeyLabel.setText(txt)
        
    def eventFilter(self, watched, event):
        """
        Method called to filter the event queue.
        
        @param watched the QObject being watched
        @param event the event that occurred
        @return always False
        """
        if event.type() == QEvent.KeyPress:
            self.keyPressEvent(event)
            return True
            
        return False
        
    def keyPressEvent(self, evt):
        """
        Private method to handle a key press event.
        
        @param evt the key event (QKeyEvent)
        """
        if evt.key() == Qt.Key_Control:
            return
        if evt.key() == Qt.Key_Meta:
            return
        if evt.key() == Qt.Key_Shift:
            return
        if evt.key() == Qt.Key_Alt:
            return
        if evt.key() == Qt.Key_Menu:
            return
    
        if self.keyIndex == 4:
            self.keyIndex = 0
            self.keys = [0, 0, 0, 0]
    
        if evt.key() == Qt.Key_Backtab and evt.modifiers() & Qt.ShiftModifier:
            self.keys[self.keyIndex] = Qt.Key_Tab
        else:
            self.keys[self.keyIndex] = evt.key()
        
        if evt.modifiers() & Qt.ShiftModifier:
            self.keys[self.keyIndex] += Qt.SHIFT
        if evt.modifiers() & Qt.ControlModifier:
            self.keys[self.keyIndex] += Qt.CTRL
        if evt.modifiers() & Qt.AltModifier:
            self.keys[self.keyIndex] += Qt.ALT
        if evt.modifiers() & Qt.MetaModifier:
            self.keys[self.keyIndex] += Qt.META
        
        self.keyIndex += 1
        
        if self.keyIndex == 1:
            self.__setKeyLabelText(QString(QKeySequence(self.keys[0])))
        elif self.keyIndex == 2:
            self.__setKeyLabelText(QString(QKeySequence(self.keys[0], self.keys[1])))
        elif self.keyIndex == 3:
            self.__setKeyLabelText(QString(QKeySequence(self.keys[0], self.keys[1],
                self.keys[2])))
        elif self.keyIndex == 4:
            self.__setKeyLabelText(QString(QKeySequence(self.keys[0], self.keys[1],
                self.keys[2], self.keys[3])))
