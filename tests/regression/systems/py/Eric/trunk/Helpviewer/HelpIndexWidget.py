# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a window for showing the QtHelp index.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from HelpTopicDialog import HelpTopicDialog

class HelpIndexWidget(QWidget):
    """
    Class implementing a window for showing the QtHelp index.
    
    @signal linkActivated(const QUrl&) emitted when an index  entry is activated
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
        
        self.__searchEdit = None
        self.__index = None
        
        self.__layout = QVBoxLayout(self)
        l = QLabel(self.trUtf8("&Look for:"))
        self.__layout.addWidget(l)
        
        self.__searchEdit = QLineEdit()
        l.setBuddy(self.__searchEdit)
        self.connect(self.__searchEdit, SIGNAL("textChanged(QString)"), 
                     self.__filterIndices)
        self.__searchEdit.installEventFilter(self)
        self.__layout.addWidget(self.__searchEdit)
        
        self.__index = self.__engine.indexWidget()
        self.__index.installEventFilter(self)
        self.connect(self.__engine.indexModel(), SIGNAL("indexCreationStarted()"), 
                     self.__disableSearchEdit)
        self.connect(self.__engine.indexModel(), SIGNAL("indexCreated()"), 
                     self.__enableSearchEdit)
        self.connect(self.__index, SIGNAL("linkActivated(const QUrl&, const QString&)"), 
                     self, SIGNAL("linkActivated(const QUrl&)"))
        self.connect(self.__index, 
                     SIGNAL("linksActivated(const QMap<QString, QUrl>&, const QString&)"),
                     self, 
                     SIGNAL("linksActivated(const QMap<QString, QUrl>&, const QString&)"))
        self.connect(self.__searchEdit, SIGNAL("returnPressed()"), 
                     self.__index, SLOT("activateCurrentItem()"))
        self.__layout.addWidget(self.__index)
        
        self.__index.viewport().installEventFilter(self)
    
    def __filterIndices(self, filter):
        """
        Private slot to filter the indices according to the given filter.
        
        @param filter filter to be used (QString)
        """
        if '*' in filter:
            self.__index.filterIndices(filter, filter)
        else:
            self.__index.filterIndices(filter)
    
    def __enableSearchEdit(self):
        """
        Private slot to enable the search edit.
        """
        self.__searchEdit.setEnabled(True)
        self.__filterIndices(self.__searchEdit.text())
    
    def __disableSearchEdit(self):
        """
        Private slot to enable the search edit.
        """
        self.__searchEdit.setEnabled(False)
    
    def focusInEvent(self, evt):
        """
        Protected method handling focus in events.
        
        @param evt reference to the focus event object (QFocusEvent)
        """
        if evt.reason() != Qt.MouseFocusReason:
            self.__searchEdit.selectAll()
            self.__searchEdit.setFocus()
    
    def eventFilter(self, watched, event):
        """
        Public method called to filter the event queue.
        
        @param watched the QObject being watched (QObject)
        @param event the event that occurred (QEvent)
        @return flag indicating whether the event was handled (boolean)
        """
        if self.__searchEdit and watched == self.__searchEdit and \
           event.type() == QEvent.KeyPress:
            idx = self.__index.currentIndex()
            if event.key() == Qt.Key_Up:
                idx = self.__index.model().index(
                    idx.row() - 1, idx.column(), idx.parent())
                if idx.isValid():
                    self.__index.setCurrentIndex(idx)
            elif event.key() == Qt.Key_Down:
                idx = self.__index.model().index(
                    idx.row() + 1, idx.column(), idx.parent())
                if idx.isValid():
                    self.__index.setCurrentIndex(idx)
            elif event.key() == Qt.Key_Escape:
                self.emit(SIGNAL("escapePressed()"))
        elif self.__index and watched == self.__index and \
             event.type() == QEvent.ContextMenu:
            idx = self.__index.indexAt(event.pos())
            if idx.isValid():
                menu = QMenu()
                curTab = menu.addAction(self.trUtf8("Open Link"))
                newTab = menu.addAction(self.trUtf8("Open Link in New Tab"))
                menu.move(self.__index.mapToGlobal(event.pos()))
                
                act = menu.exec_()
                if act == curTab:
                    self.__index.activateCurrentItem()
                elif act == newTab:
                    model = self.__index.model()
                    if model is not None:
                        keyword = model.data(idx, Qt.DisplayRole).toString()
                        links = model.linksForKeyword(keyword)
                        if len(links) == 1:
                            self.__mw.newTab(links.values()[0])
                        elif len(links) > 1:
                            dlg = HelpTopicDialog(self, keyword, links)
                            if dlg.exec_() == QDialog.Accepted:
                                self.__mw.newTab(dlg.link())
        elif self.__index and watched == self.__index.viewport() and \
             event.type() == QEvent.MouseButtonRelease:
            idx = self.__index.indexAt(event.pos())
            if idx.isValid() and event.button() == Qt.MidButton:
                model = self.__index.model()
                if model is not None:
                    keyword = model.data(idx, Qt.DisplayRole).toString()
                    links = model.linksForKeyword(keyword)
                    if len(links) == 1:
                        self.__mw.newTab(links.values()[0])
                    elif len(links) > 1:
                        dlg = HelpTopicDialog(self, keyword, links)
                        if dlg.exec_() == QDialog.Accepted:
                            self.__mw.newTab(dlg.link())
        
        return QWidget.eventFilter(self, watched, event)
