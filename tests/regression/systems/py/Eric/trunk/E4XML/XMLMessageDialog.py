# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to display XML parse messages.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_XMLMessageDialog import Ui_XMLMessageDialog


class XMLMessageDialog(QDialog, Ui_XMLMessageDialog):
    """
    Class implementing a dialog to display XML parse messages.
    """
    def __init__(self, msgs, parent = None):
        """
        Constructor
        
        @param msgs list of tuples of (message type, system id,
            line no, column no, message)
        @param parent parent object of the dialog (QWidget)
        """
        QDialog.__init__(self,parent)
        self.setupUi(self)
        
        for type, sysId, line, column, msg in msgs:
            if type == "F":
                color = QColor(Qt.red)
                self.__appendText(self.trUtf8("Fatal Error"), color)
            elif type == "E":
                color = QColor(Qt.blue)
                self.__appendText(self.trUtf8("Error"), color)
            elif type == "W":
                color = QColor(Qt.black)
                self.__appendText(self.trUtf8("Warning"), color)
            
            self.__appendText(sysId, color)
            self.__appendText(self.trUtf8("Line: %1, Column: %2")
                .arg(line).arg(column), color)
            self.__appendText(msg, color)
            
            self.__appendText("------", QColor(Qt.black))
        
        tc = self.messages.textCursor()
        tc.movePosition(QTextCursor.Start)
        self.messages.setTextCursor(tc)
        self.messages.ensureCursorVisible()

    def __appendText(self, txt, color):
        """
        Private method to append text to the end of the messages pane.
        
        @param txt text to insert (QString)
        @param color text color to be used (QColor)
        """
        if txt is not None:
            tc = self.messages.textCursor()
            tc.movePosition(QTextCursor.End)
            self.messages.setTextCursor(tc)
            self.messages.setTextColor(color)
            self.messages.insertPlainText(txt)
            self.messages.insertPlainText("\n")
