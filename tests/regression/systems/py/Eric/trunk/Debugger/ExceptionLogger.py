# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Exception Logger widget.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from KdeQt.KQApplication import e4App


class ExceptionLogger(QTreeWidget):
    """
    Class implementing the Exception Logger widget.
    
    This class displays a log of all exceptions having occured during
    a debugging session.
    
    @signal sourceFile(string, int) emitted to open a source file at a line
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent the parent widget of this widget
        """
        QTreeWidget.__init__(self, parent)
        self.setObjectName("ExceptionLogger")
        
        self.setWindowTitle(self.trUtf8("Exceptions"))
        
        self.setWordWrap(True)
        self.setRootIsDecorated(True)
        self.setHeaderLabels(QStringList() << self.trUtf8("Exception"))
        self.setSortingEnabled(False)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self,SIGNAL('customContextMenuRequested(const QPoint &)'),
                     self.__showContextMenu)
        self.connect(self,SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'),
                     self.__itemDoubleClicked)

        self.setWhatsThis(self.trUtf8(
            """<b>Exceptions Logger</b>"""
            """<p>This windows shows a trace of all exceptions, that have"""
            """ occured during the last debugging session. Initially only the"""
            """ exception type and exception message are shown. After"""
            """ the expansion of this entry, the complete call stack as reported"""
            """ by the client is show with the most recent call first.</p>"""
        ))
        
        self.menu = QMenu(self)
        self.menu.addAction(self.trUtf8("Show source"), self.__openSource)
        self.menu.addAction(self.trUtf8("Clear"), self.clear)
        self.menu.addSeparator()
        self.menu.addAction(self.trUtf8("Configure..."), self.__configure)
        
        self.backMenu = QMenu(self)
        self.backMenu.addAction(self.trUtf8("Clear"), self.clear)
        self.backMenu.addSeparator()
        self.backMenu.addAction(self.trUtf8("Configure..."), self.__configure)
        
    def __itemDoubleClicked(self, itm):
        """
        Private slot to handle the double click of an item. 
        
        @param itm the item that was double clicked(QTreeWidgetItem), ignored
        """
        self.__openSource()

    def __showContextMenu(self, coord):
        """
        Private slot to show the context menu of the listview.
        
        @param coord the global coordinates of the mouse pointer (QPoint)
        """
        itm = self.itemAt(coord)
        coord = self.mapToGlobal(coord)
        if itm is None:
            self.backMenu.popup(coord)
        else:
            self.menu.popup(coord)
            
    def addException(self, exceptionType, exceptionMessage, stackTrace):
        """
        Public slot to handle the arrival of a new exception.
        
        @param exceptionType type of exception raised (string)
        @param exceptionMessage message given by the exception (string)
        @param stackTrace list of stack entries.
        """
        itm = QTreeWidgetItem(self)
        if exceptionType is None:
            itm.setText(0,
                self.trUtf8('An unhandled exception occured.'
                            ' See the shell window for details.'))
            return
        
        if exceptionMessage == '':
            itm.setText(0, "%s" % exceptionType)
        else:
            itm.setText(0, "%s, %s" % (exceptionType, exceptionMessage))
        
        # now add the call stack, most recent call first
        for fn, ln in stackTrace:
            excitm = QTreeWidgetItem(itm)
            excitm.setText(0, "%s, %d" % (fn, ln))
            
    def debuggingStarted(self):
        """
        Public slot to clear the listview upon starting a new debugging session.
        """
        self.clear()
        
    def __openSource(self):
        """
        Private slot to handle a double click on an entry.
        """
        itm = self.currentItem()
        
        if itm.parent() is None:
            return
            
        entry = unicode(itm.text(0))
        entryList = entry.split(",")
        try:
            self.emit(SIGNAL('sourceFile'), entryList[0], int(entryList[1]))
        except (IndexError, ValueError):
            pass
        
    def __configure(self):
        """
        Private method to open the configuration dialog.
        """
        e4App().getObject("UserInterface").showPreferences("debuggerGeneralPage")
