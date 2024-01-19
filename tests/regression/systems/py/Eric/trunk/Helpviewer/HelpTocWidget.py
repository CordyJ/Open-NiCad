# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a window for showing the QtHelp TOC.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class HelpTocWidget(QWidget):
    """
    Class implementing a window for showing the QtHelp TOC.
    
    @signal linkActivated(const QUrl&) emitted when a TOC entry is activated
    @signal escapePressed() emitted when the ESC key was pressed
    """
    def __init__(self, engine, mainWindow, parent = None):
        """
        Constructor
        
        @param engine reference to the help engine (QHelpEngine)
        @param mainWindow reference to the main window object (KQMainWindow)
        @param parent reference to the parent widget (QWidget)
        """
        QWidget.__init__(self, parent)
        
        self.__engine = engine
        self.__mw = mainWindow
        self.__expandDepth = -2
        
        self.__tocWidget = self.__engine.contentWidget()
        self.__tocWidget.viewport().installEventFilter(self)
        self.__tocWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.__layout = QVBoxLayout(self)
        self.__layout.addWidget(self.__tocWidget)
        
        self.connect(self.__tocWidget, SIGNAL("customContextMenuRequested(QPoint)"), 
                     self.__showContextMenu)
        self.connect(self.__tocWidget, SIGNAL("linkActivated(const QUrl&)"), 
                     self, SIGNAL("linkActivated(const QUrl&)"))
        
        model = self.__tocWidget.model()
        self.connect(model, SIGNAL("contentsCreated()"), self.__expandTOC)
    
    def __expandTOC(self):
        """
        Private slot to expand the table of contents.
        """
        if self.__expandDepth > -2:
            self.expandToDepth(self.__expandDepth)
            self.__expandDepth = -2
    
    def expandToDepth(self, depth):
        """
        Public slot to expand the table of contents to a specific depth.
        
        @param depth depth to expand to (integer)
        """
        self.__expandDepth = depth
        if depth == -1:
            self.__tocWidget.expandAll()
        else:
            self.__tocWidget.expandToDepth(depth)
    
    def focusInEvent(self, evt):
        """
        Protected method handling focus in events.
        
        @param evt reference to the focus event object (QFocusEvent)
        """
        if evt.reason() != Qt.MouseFocusReason:
            self.__tocWidget.setFocus()
    
    def keyPressEvent(self, evt):
        """
        Protected method handling key press events.
        
        @param evt reference to the key press event (QKeyEvent)
        """
        if evt.key() == Qt.Key_Escape:
            self.emit(SIGNAL("escapePressed()"))
    
    def eventFilter(self, watched, event):
        """
        Public method called to filter the event queue.
        
        @param watched the QObject being watched (QObject)
        @param event the event that occurred (QEvent)
        @return flag indicating whether the event was handled (boolean)
        """
        if self.__tocWidget and watched == self.__tocWidget.viewport() and \
           event.type() == QEvent.MouseButtonRelease:
            if self.__tocWidget.indexAt(event.pos()).isValid() and \
               event.button() == Qt.LeftButton:
                self.itemClicked(self.__tocWidget.currentIndex())
            elif self.__tocWidget.indexAt(event.pos()).isValid() and \
                 event.button() == Qt.MidButton:
                model = self.__tocWidget.model()
                itm = model.contentItemAt(self.__tocWidget.currentIndex())
                self.__mw.newTab(itm.url())
        
        return QWidget.eventFilter(self, watched, event)
    
    def itemClicked(self, index):
        """
        Public slot handling a click of a TOC entry.
        
        @param index index of the TOC clicked (QModelIndex)
        """
        if not index.isValid():
            return
        
        model = self.__tocWidget.model()
        itm = model.contentItemAt(index)
        if itm:
            self.emit(SIGNAL("linkActivated(const QUrl&)"), itm.url())
    
    def syncToContent(self, url):
        """
        Public method to sync the TOC to the displayed page.
        
        @param url URL of the displayed page (QUrl)
        @return flag indicating a successful synchronization (boolean)
        """
        idx = self.__tocWidget.indexOf(url)
        if not idx.isValid():
            return False
        self.__tocWidget.setCurrentIndex(idx)
        return True
    
    def __showContextMenu(self, pos):
        """
        Private slot showing the context menu.
        
        @param pos position to show the menu at (QPoint)
        """
        if not self.__tocWidget.indexAt(pos).isValid():
            return
        
        menu = QMenu()
        curTab = menu.addAction(self.trUtf8("Open Link"))
        newTab = menu.addAction(self.trUtf8("Open Link in New Tab"))
        menu.move(self.__tocWidget.mapToGlobal(pos))
        
        model = self.__tocWidget.model()
        itm = model.contentItemAt(self.__tocWidget.currentIndex())
        
        act = menu.exec_()
        if act == curTab:
            self.emit(SIGNAL("linkActivated(const QUrl&)"), itm.url())
        elif act == newTab:
            self.__mw.newTab(itm.url())
