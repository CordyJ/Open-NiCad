# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the log viewer widget and the log widget.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from E4Gui.E4TabWidget import E4TabWidget

from KdeQt.KQApplication import e4App

import UI.PixmapCache
import Preferences

class LogViewer(QTextEdit):
    """
    Class providing a specialized text edit for displaying logging information.
    """
    def __init__(self, parent = None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        QTextEdit.__init__(self, parent)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setReadOnly(True)
        
        self.setWindowIcon(UI.PixmapCache.getIcon("eric.png"))
        
        # create the context menu
        self.__menu = QMenu(self)
        self.__menu.addAction(self.trUtf8('Clear'), self.clear)
        self.__menu.addAction(self.trUtf8('Copy'), self.copy)
        self.__menu.addSeparator()
        self.__menu.addAction(self.trUtf8('Select All'), self.selectAll)
        self.__menu.addSeparator()
        self.__menu.addAction(self.trUtf8("Configure..."), self.__configure)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL("customContextMenuRequested(const QPoint &)"),
            self.__handleShowContextMenu)
        
        self.cNormalFormat = self.currentCharFormat()
        self.cErrorFormat = self.currentCharFormat()
        self.cErrorFormat.setForeground(QBrush(Preferences.getUI("LogStdErrColour")))
        
    def __handleShowContextMenu(self, coord):
        """
        Private slot to show the context menu.
        
        @param coord the position of the mouse pointer (QPoint)
        """
        coord = self.mapToGlobal(coord)
        self.__menu.popup(coord)
        
    def __appendText(self, txt, error = False):
        """
        Public method to append text to the end.
        
        @param txt text to insert (QString)
        @param error flag indicating to insert error text (boolean)
        """
        tc = self.textCursor()
        tc.movePosition(QTextCursor.End)
        self.setTextCursor(tc)
        if error:
            self.setCurrentCharFormat(self.cErrorFormat)
        else:
            self.setCurrentCharFormat(self.cNormalFormat)
        self.insertPlainText(txt)
        self.ensureCursorVisible()
        
    def appendToStdout(self, txt):
        """
        Public slot to appand text to the "stdout" tab.
        
        @param txt text to be appended (string or QString)
        """
        self.__appendText(txt, error = False)
        QApplication.processEvents()
        
    def appendToStderr(self, txt):
        """
        Public slot to appand text to the "stderr" tab.
        
        @param txt text to be appended (string or QString)
        """
        self.__appendText(txt, error = True)
        QApplication.processEvents()
        
    def preferencesChanged(self):
        """
        Public slot to handle a change of the preferences.
        """
        self.cErrorFormat.setForeground(QBrush(Preferences.getUI("LogStdErrColour")))
        
    def __configure(self):
        """
        Private method to open the configuration dialog.
        """
        e4App().getObject("UserInterface").showPreferences("interfacePage")
